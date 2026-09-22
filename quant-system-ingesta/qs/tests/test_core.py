"""Tests de la lógica crítica: sincronización del libro, writer atómico y auditoría."""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from ingestion.book import LocalBook, GapError, EventType
from ingestion.writer import ParquetBuffer, DEPTH_SCHEMA, TRADE_SCHEMA
from ingestion.audit import audit_depth, read_day, compact_day, write_audit


def snap(luid=100):
    return {"lastUpdateId": luid,
            "bids": [["100.0", "5"], ["99.5", "3"], ["99.0", "2"]],
            "asks": [["100.5", "4"], ["101.0", "6"], ["101.5", "1"]]}


def ev(U, u, pu, b=None, a=None, E=1700000000000):
    return {"E": E, "U": U, "u": u, "pu": pu, "b": b or [], "a": a or []}


def mk_depth(recv, fuid, puid, et=0, b0=100.0, a0=100.5, mono=None):
    # v2: por defecto el monotónico refleja la pared (sesión sin reinicios)
    return {"recv_ts_ns": recv, "recv_mono_ns": recv if mono is None else mono,
            "event_ts_ms": 1, "first_update_id": fuid,
            "final_update_id": fuid, "prev_final_update_id": puid, "event_type": et,
            "bid_prices": [b0, 99.5], "bid_volumes": [5.0, 3.0],
            "ask_prices": [a0, 101.0], "ask_volumes": [4.0, 6.0]}


def mk_trade(i):
    return {"recv_ts_ns": i * 10 ** 9, "recv_mono_ns": i * 10 ** 9,
            "event_ts_ms": 1, "trade_ts_ms": 1,
            "agg_trade_id": i, "price": 1.0, "qty": 2.0, "is_buyer_maker": False}


def day_dir(tmp_path, symbol="T"):
    return glob.glob(str(tmp_path) + f"/{symbol}/*")[0]


class TestEmpalmeSnapshot:
    """EL EMPALME, con la regla OFICIAL de USDⓈ-M literal (mesa 2026-08-29, 6º dictamen).

    El primer evento aplicado debe cumplir `U <= L <= u`, donde L es el `lastUpdateId` del snapshot.
    Nada más. La extensión que yo habia anadido —aceptar `U == L+1` cuando `pu == L`— se RETIRA:
    se apoyaba en un barrido propio sin script ni recibo versionado, y altera la poblacion aceptada.
    Un numero sin procedencia no acredita nada, y menos si cambia lo que entra."""

    def test_el_snapshot_DENTRO_del_evento_sincroniza(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        assert bk.apply_diff(ev(98, 105, 97)) is not None          # U <= L <= u
        assert bk.synced

    def test_el_borde_exacto_U_igual_L_sincroniza(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        assert bk.apply_diff(ev(100, 105, 99)) is not None         # U == L
        assert bk.synced

    def test_el_borde_exacto_u_igual_L_sincroniza(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        assert bk.apply_diff(ev(95, 100, 94)) is not None          # u == L
        assert bk.synced

    def test_la_banda_L_MAS_UNO_YA_NO_entra(self):
        """La extension retirada. Aunque `pu == L` —es decir, aunque encadene—, la regla oficial no
        la admite y aqui se aplica LITERAL: si alguna vez vuelve, sera como cambio normativo previo
        con instrumento, recibo y refutacion propios, no como «invariante equivalente»."""
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        with pytest.raises(GapError, match="empalme"):
            bk.apply_diff(ev(101, 105, 100))                       # U == L+1 y pu == L
        assert not bk.synced

    def test_un_snapshot_VIEJO_sigue_siendo_hueco(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        with pytest.raises(GapError, match="empalme"):
            bk.apply_diff(ev(103, 108, 102))                       # U > L+1
        assert not bk.synced

    def test_lo_anterior_al_snapshot_se_descarta_sin_gritar(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        assert bk.apply_diff(ev(90, 95, 89)) is None               # u < L
        assert not bk.synced


class TestSync:
    def test_descarta_eventos_previos_al_snapshot(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        assert bk.apply_diff(ev(90, 95, 89)) is None      # u < lastUpdateId
        assert not bk.synced

    def test_primer_evento_valido_sincroniza(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        r = bk.apply_diff(ev(98, 105, 97, b=[["100.0", "7"]]))
        assert bk.synced and r.event_type == EventType.DEPTH_UPDATE
        assert bk.bids[100.0] == 7.0 and bk.last_update_id == 105

    def test_snapshot_viejo_lanza_gap(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        with pytest.raises(GapError):
            bk.apply_diff(ev(150, 160, 149))               # U > last+1

    def test_cadena_continua_ok_y_gap_detectado(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        bk.apply_diff(ev(98, 105, 97))
        bk.apply_diff(ev(106, 110, 105))                   # pu == u_anterior: ok
        with pytest.raises(GapError):
            bk.apply_diff(ev(115, 120, 114))               # pu 114 != 110

    def test_qty_cero_elimina_nivel_y_top_ordenado(self):
        bk = LocalBook("T"); bk.load_snapshot(snap(100))
        bk.apply_diff(ev(98, 105, 97, b=[["99.5", "0"]], a=[["100.4", "2"]]))
        assert 99.5 not in bk.bids
        bp, _, ap, _ = bk.top()
        assert bp == sorted(bp, reverse=True) and ap == sorted(ap)
        assert ap[0] == 100.4                              # nuevo mejor ask


class TestAudit:
    def _write(self, tmp_path, records):
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        for r in records: buf.add(r)
        buf.close()
        return day_dir(tmp_path)

    def test_dia_limpio_pass(self, tmp_path):
        recs = [mk_depth(i * 10 ** 9, 100 + i, 99 + i) for i in range(5)]
        r = audit_depth(self._write(tmp_path, recs))
        assert r["status"] == "PASS" and all(r["checks"].values())

    def test_secuencia_rota_fail(self, tmp_path):
        recs = [mk_depth(0, 100, 99), mk_depth(10 ** 9, 110, 105)]   # pu!=fuid ant.
        assert audit_depth(self._write(tmp_path, recs))["status"] == "FAIL"

    def test_libro_cruzado_fail(self, tmp_path):
        recs = [mk_depth(0, 100, 99, b0=101.0, a0=100.5)]
        r = audit_depth(self._write(tmp_path, recs))
        assert not r["checks"]["c3_no_cruzado"] and r["status"] == "FAIL"

    def test_silencio_largo_warn(self, tmp_path):
        recs = [mk_depth(0, 100, 99), mk_depth(70 * 10 ** 9, 101, 100)]
        r = audit_depth(self._write(tmp_path, recs))
        assert r["status"] == "WARN" and r["max_silence_s"] == 70.0

    def test_rebuild_no_rompe_cadena(self, tmp_path):
        recs = [mk_depth(0, 100, 99), mk_depth(10 ** 9, 100, -1, et=1),
                mk_depth(2 * 10 ** 9, 200, 150)]            # tras rebuild, cadena nueva
        r = audit_depth(self._write(tmp_path, recs))
        assert r["checks"]["c2_secuencia"] and r["n_rebuilds"] == 1


class TestWriterAtomico:
    """Writer v1.2 (ESPEC §7): parts inmutables por flush vía tmp+rename; un
    reinicio dentro del mismo día UTC nunca sobrescribe los datos previos."""

    def test_reinicio_mismo_dia_no_pierde_datos(self, tmp_path):
        b1 = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        for i in range(3): b1.add(mk_depth(i * 10 ** 9, 100 + i, 99 + i))
        b1.close()                                   # proceso 1 termina
        b2 = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        for i in range(3, 5): b2.add(mk_depth(i * 10 ** 9, 100 + i, 99 + i))
        b2.close()                                   # proceso 2 (reinicio)
        d = day_dir(tmp_path)
        t = read_day(d, "depth")
        assert t.num_rows == 5                       # nada sobrescrito
        assert t.column("recv_ts_ns").to_pylist() == [i * 10 ** 9 for i in range(5)]
        parts = sorted(os.path.basename(p) for p in glob.glob(d + "/depth-*.parquet"))
        assert parts == ["depth-00000.parquet", "depth-00001.parquet"]

    def test_flush_atomico_sin_tmp_residual(self, tmp_path):
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        buf.add(mk_depth(0, 100, 99)); buf.flush()
        buf.add(mk_depth(10 ** 9, 101, 100)); buf.flush()
        buf.close()
        d = day_dir(tmp_path)
        assert sorted(os.listdir(d)) == ["depth-00000.parquet", "depth-00001.parquet"]
        assert read_day(d, "depth").num_rows == 2

    def test_convive_con_compactado_previo(self, tmp_path):
        # {kind}.parquet ya compactado + parts nuevos del mismo día (v2)
        import pyarrow as pa, pyarrow.parquet as pq
        d = tmp_path / "T" / "1970-01-01"     # día UTC de los recv_ts_ns usados
        d.mkdir(parents=True)
        previo = [mk_depth(0, 100, 99), mk_depth(10 ** 9, 101, 100)]
        cols = {f.name: [r[f.name] for r in previo] for f in DEPTH_SCHEMA}
        pq.write_table(pa.table(cols, schema=DEPTH_SCHEMA), str(d / "depth.parquet"))
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        buf.add(mk_depth(2 * 10 ** 9, 102, 101))
        buf.close()
        t = read_day(str(d), "depth")
        assert t.num_rows == 3                       # compactado primero, part después
        assert t.column("recv_ts_ns").to_pylist() == [0, 10 ** 9, 2 * 10 ** 9]


class TestParticionPorDia:
    """Writer v1.3 (ESPEC §5/§7): el día de cada registro se deriva de su
    recv_ts_ns; un flush que cruza la medianoche UTC publica un part por día,
    cada uno en su directorio."""

    def test_buffer_con_dos_dias_separa_directorios(self, tmp_path):
        from ingestion.writer import DAY_NS
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        buf.add(mk_depth(DAY_NS - 2 * 10 ** 9, 100, 99))    # día 1, 23:59:58
        buf.add(mk_depth(DAY_NS - 10 ** 9, 101, 100))       # día 1, 23:59:59
        buf.add(mk_depth(DAY_NS + 10 ** 9, 102, 101))       # día 2, 00:00:01
        buf.flush()                                          # un único flush
        days = sorted(os.path.basename(p) for p in glob.glob(str(tmp_path) + "/T/*"))
        assert days == ["1970-01-01", "1970-01-02"]
        t1 = read_day(str(tmp_path / "T" / "1970-01-01"), "depth")
        t2 = read_day(str(tmp_path / "T" / "1970-01-02"), "depth")
        assert t1.column("recv_ts_ns").to_pylist() == [DAY_NS - 2 * 10 ** 9,
                                                       DAY_NS - 10 ** 9]
        assert t2.column("recv_ts_ns").to_pylist() == [DAY_NS + 10 ** 9]
        # el flush siguiente, ya dentro del día 2, continúa su numeración
        buf.add(mk_depth(DAY_NS + 2 * 10 ** 9, 103, 102))
        buf.close()
        parts = sorted(os.path.basename(p) for p in
                       glob.glob(str(tmp_path / "T" / "1970-01-02") + "/depth-*.parquet"))
        assert parts == ["depth-00000.parquet", "depth-00001.parquet"]


class TestCompactacion:
    """Cierre de día (ESPEC §6, v1.2): parts → un único {kind}.parquet, atómico
    e idempotente; la auditoría sigue PASS sobre el compactado."""

    def _two_runs(self, tmp_path):
        b1 = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        for i in range(3): b1.add(mk_depth(i * 10 ** 9, 100 + i, 99 + i))
        b1.close()
        b2 = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        for i in range(3, 5): b2.add(mk_depth(i * 10 ** 9, 100 + i, 99 + i))
        b2.close()
        return day_dir(tmp_path)

    def test_compacta_y_audita_pass(self, tmp_path):
        d = self._two_runs(tmp_path)
        res = compact_day(d, "depth")
        assert res["compactado"] and res["n_parts"] == 2 and res["n_rows"] == 5
        assert glob.glob(d + "/depth-*.parquet") == []   # parts borrados
        t = read_day(d, "depth")
        assert t.num_rows == 5
        assert t.column("recv_ts_ns").to_pylist() == [i * 10 ** 9 for i in range(5)]
        assert audit_depth(d)["status"] == "PASS"

    def test_interrumpida_no_duplica(self, tmp_path):
        d = self._two_runs(tmp_path)
        parts = sorted(glob.glob(d + "/depth-*.parquet"))
        with open(parts[0], "rb") as f:
            saved = f.read()
        compact_day(d, "depth")
        # crash simulado: compactado ya publicado pero un part sin borrar
        with open(parts[0], "wb") as f:
            f.write(saved)
        res = compact_day(d, "depth")
        assert res["n_parts"] == 0 and res["n_rows"] == 5   # solo limpia
        assert read_day(d, "depth").num_rows == 5           # sin duplicados
        assert glob.glob(d + "/depth-*.parquet") == []

    def test_write_audit_compacta_y_cuenta_trades(self, tmp_path):
        d = self._two_runs(tmp_path)
        bt = ParquetBuffer(str(tmp_path), "T", "trades", TRADE_SCHEMA)
        for i in range(7): bt.add(mk_trade(i))
        bt.close()
        out = os.path.join(d, "audit.json")
        res = write_audit(d, out)
        assert res["status"] == "PASS" and res["n_events"] == 5
        assert res["n_trades"] == 7 and res["n_tmp_huerfanos"] == 0
        assert res["compactacion"]["depth"]["compactado"]
        assert os.path.exists(out)
        assert sorted(os.listdir(d)) == ["audit.json", "depth.parquet",
                                         "trades.parquet"]

    def test_reinicio_tras_compactacion_intradia_no_pierde_datos(self, tmp_path):
        # hallazgo code-reviewer: compactar a mediodía + reinicio reutilizaba
        # índices de parts ya absorbidos → la siguiente compactación los borraba
        d = self._two_runs(tmp_path)                  # parts 00000 y 00001
        compact_day(d, "depth")                       # compactación intradía
        b3 = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        b3.add(mk_depth(10 * 10 ** 9, 200, 199))      # reinicio el mismo día
        b3.close()
        parts = sorted(os.path.basename(p)
                       for p in glob.glob(d + "/depth-*.parquet"))
        assert parts == ["depth-00002.parquet"]       # numera TRAS los absorbidos
        compact_day(d, "depth")
        assert read_day(d, "depth").num_rows == 6     # 5 + 1, nada perdido


class TestFeedRebuild:
    """Integración del feed (ESPEC §3 paso 4 / §7): reconexión — por gap o por
    cierre limpio del WS a mitad de sesión — → re-snapshot → marcador BOOK_REBUILD
    → auditoría C2 PASS. Sin red real: WS y snapshot simulados, pero ejecutando el
    run_symbol_feed de producción."""

    @staticmethod
    def _dev(U, u, pu):
        return {**ev(U, u, pu), "e": "depthUpdate"}

    def _run_scripted(self, monkeypatch, snapshots, conns):
        """Ejecuta run_symbol_feed contra conexiones WS guionizadas; devuelve los
        BookRecord emitidos. stop se activa al agotarse la última conexión, de modo
        que entre conexiones intermedias el feed reconecta como en producción."""
        import asyncio, json
        import aiohttp as real_aiohttp
        from ingestion import feed_binance

        stop = asyncio.Event()
        conns = [list(c) for c in conns]
        snapshots = list(snapshots)

        class FakeMsg:
            type = real_aiohttp.WSMsgType.TEXT
            def __init__(self, payload): self.data = json.dumps({"data": payload})

        class FakeWS:
            def __init__(self, msgs): self._msgs = msgs
            async def __aenter__(self): return self
            async def __aexit__(self, *a): return False
            def __aiter__(self): return self
            async def __anext__(self):
                await asyncio.sleep(0)          # cede control → corre snap_task
                if not self._msgs:
                    if not conns:                # última conexión agotada → parar
                        stop.set()
                    raise StopAsyncIteration     # si quedan: reconexión limpia
                return FakeMsg(self._msgs.pop(0))

        class FakeSession:
            async def __aenter__(self): return self
            async def __aexit__(self, *a): return False
            def ws_connect(self, *a, **kw): return FakeWS(conns.pop(0))

        async def fake_snapshot(session, symbol): return snapshots.pop(0)

        monkeypatch.setattr(feed_binance.aiohttp, "ClientSession", lambda: FakeSession())
        monkeypatch.setattr(feed_binance, "fetch_snapshot", fake_snapshot)

        async def run():
            dq = asyncio.Queue()
            await feed_binance.run_symbol_feed("T", dq, stop)
            recs = []
            while not dq.empty():
                recs.append(dq.get_nowait())
            return recs

        return asyncio.run(asyncio.wait_for(run(), 10))

    def _assert_dos_cadenas_validas(self, tmp_path, recs):
        # 2 rebuilds (sync inicial + resync) intercalados con la cadena correcta
        assert [r.event_type for r in recs] == [1, 0, 0, 1, 0, 0]
        assert [r.final_update_id for r in recs] == [100, 105, 110, 200, 205, 210]
        # y la auditoría acepta la discontinuidad gracias al marcador
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        for r in recs: buf.add(r)
        buf.close()
        res = audit_depth(day_dir(tmp_path))
        assert res["checks"]["c2_secuencia"] and res["n_rebuilds"] == 2
        assert res["status"] == "PASS"

    def test_gap_emite_rebuild_y_audit_c2_pasa(self, tmp_path, monkeypatch):
        recs = self._run_scripted(
            monkeypatch, snapshots=[snap(100), snap(200)],
            conns=[
                # conexión 1: 2 diffs encadenados + 1 con pu roto (114≠110) → GapError
                [self._dev(98, 105, 97), self._dev(106, 110, 105),
                 self._dev(115, 120, 114)],
                # conexión 2 (tras gap): re-snapshot y cadena nueva
                [self._dev(198, 205, 197), self._dev(206, 210, 205)],
            ])
        self._assert_dos_cadenas_validas(tmp_path, recs)

    def test_desconexion_limpia_a_mitad_resincroniza(self, tmp_path, monkeypatch):
        # el WS se cierra SIN gap a mitad de sesión (caída de red, cierre del server)
        # → reconexión + re-snapshot + marcador; la cadena nueva no encadena con la
        # vieja (pu 197 ≠ 110) y C2 debe aceptarlo igualmente
        recs = self._run_scripted(
            monkeypatch, snapshots=[snap(100), snap(200)],
            conns=[
                [self._dev(98, 105, 97), self._dev(106, 110, 105)],  # cierre limpio
                [self._dev(198, 205, 197), self._dev(206, 210, 205)],
            ])
        self._assert_dos_cadenas_validas(tmp_path, recs)


class TestTradeWS:
    """v2.1: trades por WS aggTrade en ruta /market, con el watermark contiguo
    compartido (duplicados saltados; tras hueco NO se encola: lo repone REST)."""

    def test_acepta_contiguos_salta_duplicados_y_huecos(self, monkeypatch):
        import asyncio, json
        import aiohttp as real_aiohttp
        from ingestion import feed_binance as fb

        stop = asyncio.Event()
        msgs = [
            {"e": "aggTrade", "E": 1, "T": 1, "a": 5, "p": "1.0", "q": "2", "m": False},
            {"e": "aggTrade", "E": 2, "T": 2, "a": 6, "p": "1.1", "q": "1", "m": True},
            {"e": "aggTrade", "E": 3, "T": 3, "a": 6, "p": "1.1", "q": "1", "m": True},
            {"e": "aggTrade", "E": 4, "T": 4, "a": 9, "p": "1.2", "q": "3", "m": False},
        ]

        class FakeMsg:
            type = real_aiohttp.WSMsgType.TEXT
            def __init__(self, payload): self.data = json.dumps({"data": payload})

        class FakeWS:
            def __init__(self): self._m = list(msgs)
            async def __aenter__(self): return self
            async def __aexit__(self, *a): return False
            def __aiter__(self): return self
            async def __anext__(self):
                await asyncio.sleep(0)
                if not self._m:
                    stop.set()
                    raise StopAsyncIteration
                return FakeMsg(self._m.pop(0))

        class FakeSession:
            async def __aenter__(self): return self
            async def __aexit__(self, *a): return False
            def ws_connect(self, *a, **kw): return FakeWS()

        monkeypatch.setattr(fb.aiohttp, "ClientSession", lambda: FakeSession())
        st = fb.TradeState()
        q = asyncio.Queue()

        async def run():
            await fb.run_trade_ws("T", q, stop, trade_state=st)
            out = []
            while not q.empty():
                out.append(q.get_nowait()["agg_trade_id"])
            return out

        ids = asyncio.run(asyncio.wait_for(run(), 10))
        assert ids == [5, 6]                      # dup saltado; 9 fuera (hueco 7-8)
        assert st.last_id == 6 and st.ws_max == 9 and st.hole


class TestTradeFallback:
    """Fallback REST de trades (ESPEC §3, v1.1/v1.4): activación por silencio del
    WS o por hueco de ids, recuperación vía REST y watermark contiguo de dedup."""

    @staticmethod
    def _mock_rest(monkeypatch, pages):
        from ingestion import feed_binance as fb

        class FakeResp:
            def __init__(self, data): self._d = data
            async def __aenter__(self): return self
            async def __aexit__(self, *a): return False
            def raise_for_status(self): pass
            async def json(self): return self._d

        class FakeSession:
            async def __aenter__(self): return self
            async def __aexit__(self, *a): return False
            def get(self, url, params=None):
                return FakeResp(pages.pop(0) if pages else [])

        monkeypatch.setattr(fb.aiohttp, "ClientSession", lambda: FakeSession())

    @staticmethod
    def _run_until(state, q, stop, fb_kwargs, objetivo):
        import asyncio
        from ingestion import feed_binance as fb

        async def run():
            task = asyncio.create_task(
                fb.run_trade_fallback("T", q, state, stop, **fb_kwargs))
            for _ in range(300):
                if state.last_id >= objetivo:
                    break
                await asyncio.sleep(0.01)
            stop.set()
            await task

        asyncio.run(asyncio.wait_for(run(), 10))
        ids = []
        while not q.empty():
            ids.append(q.get_nowait()["agg_trade_id"])
        return ids

    def test_recupera_y_deduplica(self, monkeypatch):
        import asyncio, time
        from ingestion import feed_binance as fb
        # dos páginas REST; la segunda solapa el id 2 → debe deduplicarse
        self._mock_rest(monkeypatch, [
            [{"a": 1, "p": "1.0", "q": "2", "T": 1000, "m": False},
             {"a": 2, "p": "1.1", "q": "3", "T": 1001, "m": True}],
            [{"a": 2, "p": "1.1", "q": "3", "T": 1001, "m": True},
             {"a": 3, "p": "1.2", "q": "1", "T": 1002, "m": False}],
        ])
        state = fb.TradeState()
        state.ws_ts = time.time() - 999           # pared: startTime del REST
        state.ws_mono = time.monotonic() - 999    # v2: el silencio se mide aquí
        ids = self._run_until(state, asyncio.Queue(), asyncio.Event(),
                              {"silence": 1, "poll": 0.01}, objetivo=3)
        assert ids == [1, 2, 3]                   # todos recuperados, sin duplicados
        assert state.last_id == 3

    def test_watermark_ws_contiguo(self):
        """Hallazgo code-reviewer (crítico): el WS al revivir tras un hueco no debe
        avanzar el watermark saltando ids — eso perdía el tramo no repuesto."""
        from ingestion.feed_binance import TradeState
        st = TradeState()
        assert st.ws_accept(5) is True and st.last_id == 5    # primer trade
        assert st.ws_accept(6) is True                        # contiguo: encolar
        assert st.ws_accept(6) is False                       # duplicado
        assert st.ws_accept(9) is False and st.last_id == 6   # hueco 7-8: NO encolar
        assert st.hole                                        # el poller debe actuar
        st.last_id = 9                                        # REST repuso 7,8,9
        assert not st.hole
        assert st.ws_accept(10) is True                       # normalidad contigua

    def test_rellena_hueco_con_ws_vivo(self, monkeypatch):
        """El poller actúa aunque el WS esté vivo si hay hueco (state.hole) y
        repone el tramo faltante en orden desde el watermark."""
        import asyncio, time
        from ingestion import feed_binance as fb
        self._mock_rest(monkeypatch, [
            [{"a": i, "p": "1.0", "q": "1", "T": 1000 + i, "m": False}
             for i in (7, 8, 9)],
        ])
        state = fb.TradeState()
        state.ws_mono = time.monotonic()          # WS vivo: sin silencio (v2)
        state.last_id, state.ws_max = 6, 9        # hueco 7-9 (ws_accept lo marcó)
        ids = self._run_until(state, asyncio.Queue(), asyncio.Event(),
                              {"silence": 999, "poll": 0.01}, objetivo=9)
        assert ids == [7, 8, 9]                   # tramo repuesto en orden
        assert state.last_id == 9 and not state.hole


class TestAlerta:
    def test_send_alert_noop_sin_config(self, monkeypatch):
        """Sin credenciales en entorno: no-op silencioso, no lanza ni usa red."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
        import asyncio
        from ingestion.main import send_alert
        asyncio.run(send_alert("prueba"))                  # no debe lanzar

    def test_debounce_una_alerta_caida_y_una_recuperacion(self, monkeypatch):
        """ESPEC §7 / SETUP_CODE item 9: con send_alert mockeado, una caída
        prolongada produce exactamente 1 alerta de caída y, al volver el stream,
        exactamente 1 de recuperación (sin spam en latidos intermedios)."""
        import asyncio
        import time as treal
        from ingestion import main as m

        sent = []
        async def fake_alert(text): sent.append(text)
        monkeypatch.setattr(m, "send_alert", fake_alert)
        monkeypatch.setattr(m, "HEARTBEAT_SECS", 0.02)
        monkeypatch.setattr(m, "ALERT_SILENCE_SECS", 0.15)

        last_seen = {"X:depth": treal.monotonic()}   # v2: liveness monotónico
        stop = asyncio.Event()

        async def run():
            task = asyncio.create_task(m.heartbeat(last_seen, stop))
            await asyncio.sleep(0.4)             # X cae: varios latidos lo ven mudo
            for _ in range(12):                  # X se recupera y se mantiene vivo
                last_seen["X:depth"] = treal.monotonic()
                await asyncio.sleep(0.02)
            stop.set()
            await task

        asyncio.run(asyncio.wait_for(run(), 10))
        assert len(sent) == 2, f"esperaba [caída, recuperación], llegó: {sent}"
        assert sent[0].startswith("⚠️") and "X:depth" in sent[0]
        assert sent[1].startswith("✅") and "X:depth" in sent[1]


class TestRetention:
    """tools/retention.py (ESPEC §9 v1.4): borra solo días auditados y fuera de la
    ventana protegida; por antigüedad y por presión de disco, antiguos primero."""

    def _mk_day(self, root, sym, day, audited=True, nbytes=1000, backed=True):
        d = root / sym / day
        d.mkdir(parents=True)
        (d / "depth.parquet").write_bytes(b"x" * nbytes)
        if audited:
            (d / "audit.json").write_text("{}")
        if backed:
            (d / ".backed_up").write_text("2026-06-12T00:30:00Z")
        return str(d)

    def test_sin_respaldo_jamas_se_borra(self, tmp_path):
        # candado v2.2: auditado pero SIN .backed_up → intocable, incluso viejo
        # y bajo presión de disco
        import time as t
        from tools.retention import plan_retention
        now = t.time()
        self._mk_day(tmp_path, "T", "2020-01-01", backed=False)
        respaldado = self._mk_day(tmp_path, "T", "2020-02-01", backed=True)
        plan = plan_retention(str(tmp_path), max_days=30, min_free_gb=1,
                              min_keep_days=7, now=now, disk_free_bytes=0)
        assert plan == [respaldado]      # el no respaldado ni aparece

    def test_marcador_obsoleto_protege_de_borrado(self, tmp_path):
        # hallazgo CRÍTICO code-reviewer: día respaldado y luego recompactado/
        # cambiado (remoto desfasado) NO debe borrarse aunque tenga .backed_up
        import time as t
        from tools.retention import plan_retention
        now = t.time()
        d = self._mk_day(tmp_path, "T", "2020-01-01", backed=True)
        os.utime(os.path.join(d, ".backed_up"), (1000, 1000))   # marcador viejo
        (tmp_path / "T" / "2020-01-01" / "depth-00099.parquet").write_bytes(b"z")
        plan = plan_retention(str(tmp_path), max_days=30, min_free_gb=1,
                              min_keep_days=7, now=now, disk_free_bytes=0)
        assert plan == []                # marcador obsoleto = no respaldado

    def test_borra_viejos_auditados_y_protege_el_resto(self, tmp_path):
        import time as t
        from tools.retention import plan_retention
        now = t.time()
        viejo_aud = self._mk_day(tmp_path, "T", "2020-01-01")
        self._mk_day(tmp_path, "T", "2020-02-01", audited=False)   # sin auditar
        self._mk_day(tmp_path, "T", t.strftime("%Y-%m-%d", t.gmtime(now - 86400)))
        plan = plan_retention(str(tmp_path), max_days=30, min_free_gb=0,
                              min_keep_days=7, now=now)
        assert plan == [viejo_aud]      # ni el no-auditado ni el reciente

    def test_presion_de_disco_borra_antiguos_hasta_liberar(self, tmp_path):
        import time as t
        from tools.retention import plan_retention
        now = t.time()
        d1 = self._mk_day(tmp_path, "T", "2020-01-01", nbytes=1000)
        d2 = self._mk_day(tmp_path, "T", "2021-01-01", nbytes=1000)
        self._mk_day(tmp_path, "T", t.strftime("%Y-%m-%d", t.gmtime(now - 86400)))
        # sin presión y sin antigüedad → nada
        assert plan_retention(str(tmp_path), 10_000, 0, 7, now=now) == []
        # faltan ~900 bytes → basta el día más antiguo
        plan = plan_retention(str(tmp_path), 10_000, 900 / 2 ** 30, 7, now=now,
                              disk_free_bytes=0)
        assert plan == [d1]
        # faltan ~1500 → caen los dos más antiguos, el reciente queda protegido
        plan = plan_retention(str(tmp_path), 10_000, 1500 / 2 ** 30, 7, now=now,
                              disk_free_bytes=0)
        assert plan == [d1, d2]


class TestAuditV2:
    """ESPEC v2.0: C1 sobre recv_mono_ns con exención BOOK_REBUILD, retrocesos de
    pared informativos (salud NTP) y check c0 de versión de esquema."""

    def _write(self, tmp_path, records):
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA)
        for r in records: buf.add(r)
        buf.close()
        return day_dir(tmp_path)

    def test_reinicio_resetea_mono_con_marcador_pass(self, tmp_path):
        recs = [mk_depth(0, 100, 99, mono=10 ** 12),
                mk_depth(10 ** 9, 101, 100, mono=2 * 10 ** 12),
                # reinicio de proceso: marcador de arranque + monotónico casi a cero
                mk_depth(2 * 10 ** 9, 101, -1, et=1, mono=5),
                mk_depth(3 * 10 ** 9, 200, 150, mono=10)]
        r = audit_depth(self._write(tmp_path, recs))
        assert r["checks"]["c1_monotonia"] and r["status"] == "PASS"

    def test_mono_retrocede_sin_marcador_fail(self, tmp_path):
        recs = [mk_depth(0, 100, 99, mono=2 * 10 ** 12),
                mk_depth(10 ** 9, 101, 100, mono=10 ** 12)]   # retrocede sin et=1
        r = audit_depth(self._write(tmp_path, recs))
        assert not r["checks"]["c1_monotonia"] and r["status"] == "FAIL"

    def test_retroceso_de_pared_es_informativo(self, tmp_path):
        # step NTP hacia atrás: la pared retrocede, el monotónico no → día VÁLIDO
        recs = [mk_depth(5 * 10 ** 9, 100, 99, mono=1),
                mk_depth(2 * 10 ** 9, 101, 100, mono=2),
                mk_depth(6 * 10 ** 9, 102, 101, mono=3)]
        r = audit_depth(self._write(tmp_path, recs))
        assert r["status"] == "PASS" and r["wall_regressions"] == 1

    def test_dia_legacy_v1_no_crashea(self, tmp_path):
        # hallazgo code-reviewer: un día v1 (sin recv_mono_ns ni qs_schema) debe
        # dar FAIL limpio por c0, no reventar en concat/columnas antes de reportar
        import pyarrow as pa, pyarrow.parquet as pq
        d = tmp_path / "T" / "1970-01-01"
        d.mkdir(parents=True)
        v1 = pa.schema([("recv_ts_ns", pa.int64()), ("final_update_id", pa.int64())])
        pq.write_table(pa.table({"recv_ts_ns": [0], "final_update_id": [100]},
                                schema=v1), str(d / "depth.parquet"))
        r = audit_depth(str(d))                       # no debe lanzar
        assert not r["checks"]["c0_esquema"] and r["status"] == "FAIL"

    def test_exceso_de_rebuilds_degrada_a_warn(self, tmp_path):
        # ESPEC §6.2: >5 rebuilds/día = WARN del día (no solo rebuild_level)
        recs, fuid = [], 100
        for i in range(7):                            # 7 marcadores et=1
            recs.append(mk_depth(2 * i * 10 ** 9, fuid, -1, et=1, mono=10 * i + 1))
            fuid += 10
            recs.append(mk_depth((2 * i + 1) * 10 ** 9, fuid, fuid - 1,
                                 mono=10 * i + 2))
            fuid += 10
        r = audit_depth(self._write(tmp_path, recs))
        assert r["n_rebuilds"] == 7 and r["status"] == "WARN"

    def test_c0_fichero_sin_version_fail(self, tmp_path):
        import pyarrow as pa, pyarrow.parquet as pq
        d = self._write(tmp_path, [mk_depth(0, 100, 99)])
        sin_meta = DEPTH_SCHEMA.remove_metadata()
        rec = mk_depth(10 ** 9, 101, 100)
        cols = {f.name: [rec[f.name]] for f in sin_meta}
        pq.write_table(pa.table(cols, schema=sin_meta),
                       os.path.join(d, "depth-99999.parquet"))
        r = audit_depth(d)
        assert not r["checks"]["c0_esquema"] and r["status"] == "FAIL"


class TestSupervisor:
    """ESPEC §7 v2.0: un task crítico que muere se relanza con backoff y alerta;
    cuando el factory termina con stop activo, el supervisor sale limpio."""

    def test_relanza_tras_muerte_y_alerta(self, monkeypatch):
        import asyncio
        from ingestion import main as m
        sent = []
        async def fake_alert(text): sent.append(text)
        monkeypatch.setattr(m, "send_alert", fake_alert)
        stop = asyncio.Event()
        vidas = []
        async def factory():
            vidas.append(1)
            if len(vidas) < 3:
                raise RuntimeError("boom")
            stop.set()                       # tercera vida: el sistema para
        asyncio.run(asyncio.wait_for(
            m.supervise("t", factory, stop, max_backoff=1), 15))
        assert len(vidas) == 3
        assert len(sent) == 2 and all("murió" in s for s in sent)


class TestFlushExecutor:
    """ESPEC §7 v2.0: drain escribe vía thread executor; si la escritura falla,
    las filas vuelven al buffer y se reintenta (cero pérdida silenciosa)."""

    def test_drain_escribe_via_executor(self, tmp_path, monkeypatch):
        import asyncio
        from ingestion import main as m
        from ingestion import writer as w
        monkeypatch.setattr(w, "FLUSH_ROWS", 2)
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA,
                            auto_flush=False)
        stop, q, seen = asyncio.Event(), asyncio.Queue(), {}
        async def run():
            for i in range(3):
                q.put_nowait(mk_depth(i * 10 ** 9, 100 + i, 99 + i))
            task = asyncio.create_task(m.drain(q, buf, seen, "T:depth", stop))
            await asyncio.sleep(0.2)
            stop.set()
            await task
        asyncio.run(asyncio.wait_for(run(), 10))
        d = day_dir(tmp_path)
        assert read_day(d, "depth").num_rows == 3
        assert glob.glob(d + "/*.tmp") == []

    def test_fallo_de_escritura_no_pierde_filas(self, tmp_path, monkeypatch):
        import asyncio
        from ingestion import main as m
        from ingestion import writer as w
        monkeypatch.setattr(w, "FLUSH_ROWS", 1)
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA,
                            auto_flush=False)
        fallos = []
        original = buf.write_rows
        def flaky(rows):
            if not fallos and rows:
                fallos.append(len(rows))
                raise OSError("disco lleno simulado")
            original(rows)
        monkeypatch.setattr(buf, "write_rows", flaky)
        stop, q, seen = asyncio.Event(), asyncio.Queue(), {}
        async def run():
            q.put_nowait(mk_depth(0, 100, 99))
            q.put_nowait(mk_depth(10 ** 9, 101, 100))
            task = asyncio.create_task(m.drain(q, buf, seen, "T:depth", stop))
            # poll DETERMINISTA: esperar a que el reintento publique las 2 filas (o timeout ~4s),
            # NO un sleep fijo — el sleep fijo se caía bajo la carga del suite completo (fix 2026-07-06).
            for _ in range(200):
                await asyncio.sleep(0.02)
                try:
                    if read_day(day_dir(tmp_path), "depth").num_rows == 2:
                        break
                except Exception:
                    pass
            stop.set()
            await task
        asyncio.run(asyncio.wait_for(run(), 15))
        assert fallos == [1]                                   # 1º intento falló
        assert read_day(day_dir(tmp_path), "depth").num_rows == 2  # nada perdido

    def test_fallo_multidia_solo_reintenta_lo_no_publicado(self, tmp_path):
        # hallazgo code-reviewer: reintentar el batch completo tras fallar el 2º
        # día duplicaba el 1º (silencioso en trades). PartialWriteError.pending
        # debe contener SOLO lo no publicado.
        from ingestion.writer import DAY_NS, PartialWriteError
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA,
                            auto_flush=False)
        rows = [mk_depth(DAY_NS - 10 ** 9, 100, 99),     # día 1970-01-01
                mk_depth(DAY_NS + 10 ** 9, 101, 100)]    # día 1970-01-02
        original = buf._write_part
        def flaky(day, batch):
            if day == "1970-01-02" and not getattr(flaky, "ya_fallo", False):
                flaky.ya_fallo = True
                raise OSError("disco lleno simulado")
            original(day, batch)
        buf._write_part = flaky
        with pytest.raises(PartialWriteError) as exc:
            buf.write_rows(rows)
        assert [r["final_update_id"] for r in exc.value.pending] == [101]
        buf.write_rows(exc.value.pending)            # reintento de lo pendiente
        t1 = read_day(str(tmp_path / "T" / "1970-01-01"), "depth")
        t2 = read_day(str(tmp_path / "T" / "1970-01-02"), "depth")
        assert t1.num_rows == 1 and t2.num_rows == 1   # sin duplicados

    def test_alerta_al_romperse_y_recuperarse_la_escritura(self, tmp_path,
                                                           monkeypatch):
        # hallazgo code-reviewer (alta): un disco roto debe ALERTAR (debounced),
        # no solo loguear — last_seen mide ingesta, no persistencia
        import asyncio
        from ingestion import main as m
        from ingestion import writer as w
        monkeypatch.setattr(w, "FLUSH_ROWS", 1)
        sent = []
        async def fake_alert(text): sent.append(text)
        monkeypatch.setattr(m, "send_alert", fake_alert)
        buf = ParquetBuffer(str(tmp_path), "T", "depth", DEPTH_SCHEMA,
                            auto_flush=False)
        fallos = []
        original = buf.write_rows
        def flaky(rows):
            if not fallos and rows:
                fallos.append(1)
                raise OSError("disco lleno simulado")
            original(rows)
        monkeypatch.setattr(buf, "write_rows", flaky)
        stop, q, seen = asyncio.Event(), asyncio.Queue(), {}
        async def run():
            q.put_nowait(mk_depth(0, 100, 99))
            q.put_nowait(mk_depth(10 ** 9, 101, 100))
            task = asyncio.create_task(m.drain(q, buf, seen, "T:depth", stop))
            await asyncio.sleep(0.3)
            stop.set()
            await task
        asyncio.run(asyncio.wait_for(run(), 10))
        assert any(s.startswith("⚠️") and "escritura" in s for s in sent)
        assert any(s.startswith("✅") and "recuperada" in s for s in sent)
        assert read_day(day_dir(tmp_path), "depth").num_rows == 2


class TestBackup:
    """tools/backup.py (ESPEC §9 v2.2): selección de días cerrados+auditados y
    marcador .backed_up SOLO tras transferencia verificada."""

    def _mk(self, root, sym, day, audited=True, marked=False):
        d = root / sym / day
        d.mkdir(parents=True)
        (d / "depth.parquet").write_bytes(b"x" * 100)
        if audited:
            (d / "audit.json").write_text("{}")
        if marked:
            (d / ".backed_up").write_text("x")
        return str(d)

    def test_seleccion_cerrados_auditados_sin_marcar(self, tmp_path):
        from tools.backup import dias_pendientes
        viejo = self._mk(tmp_path, "T", "2026-06-10")
        self._mk(tmp_path, "T", "2026-06-09", audited=False)   # sin auditar
        self._mk(tmp_path, "T", "2026-06-08", marked=True)     # ya respaldado
        self._mk(tmp_path, "T", "2026-06-12")                  # día en curso
        assert dias_pendientes(str(tmp_path), hoy="2026-06-12") == [viejo]

    def test_marcador_solo_tras_verificacion_limpia(self, tmp_path):
        import subprocess
        from tools.backup import respaldar_dia, MARKER
        d = self._mk(tmp_path, "T", "2026-06-10")
        calls = []
        def fake_ok(args, timeout=900):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
        assert respaldar_dia(d, "u@host:dest", 23, runner=fake_ok) is True
        assert os.path.exists(os.path.join(d, MARKER))
        assert len(calls) == 2                  # transferencia + verificación

    def test_verificacion_sucia_no_marca(self, tmp_path):
        import subprocess
        from tools.backup import respaldar_dia, MARKER
        d = self._mk(tmp_path, "T", "2026-06-10")
        def fake(args, timeout=900):
            out = ">f..t.... depth.parquet\n" if "--dry-run" in args else ""
            return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
        assert respaldar_dia(d, "u@host:dest", 23, runner=fake) is False
        assert not os.path.exists(os.path.join(d, MARKER))

    def test_marcador_obsoleto_reincluye_dia(self, tmp_path):
        # hallazgo code-reviewer: un part tardío (incidencia) tras respaldar debe
        # re-disparar el respaldo, no quedar fuera para siempre
        from tools.backup import dias_pendientes
        d = self._mk(tmp_path, "T", "2026-06-10", marked=True)
        os.utime(os.path.join(d, ".backed_up"), (1000, 1000))   # marcador viejo
        (tmp_path / "T" / "2026-06-10" / "trades-00099.parquet").write_bytes(b"z")
        assert dias_pendientes(str(tmp_path), hoy="2026-06-12") == [d]

    def test_marcador_fresco_no_reincluye(self, tmp_path):
        from tools.backup import dias_pendientes
        self._mk(tmp_path, "T", "2026-06-10", marked=True)      # .backed_up el último
        assert dias_pendientes(str(tmp_path), hoy="2026-06-12") == []

    def test_remote_sin_colon_se_detecta(self):
        # footgun 2026-06-13: remote sin ':' = ruta local (rsync fingiría éxito)
        from tools.backup import remote_es_remoto
        assert remote_es_remoto("<STORAGEBOX_USER>@<STORAGEBOX_HOST>:quant-data")
        assert not remote_es_remoto("<STORAGEBOX_USER>@<STORAGEBOX_HOST>")
        assert not remote_es_remoto("/algun/path/local")

    def test_dias_huerfanos_sin_auditar(self, tmp_path):
        import calendar
        from tools.backup import dias_huerfanos
        now = calendar.timegm((2026, 6, 12, 12, 0, 0))
        self._mk(tmp_path, "T", "2026-06-05", audited=False)    # 7d, sin auditar
        self._mk(tmp_path, "T", "2026-06-11", audited=False)    # 1d, dentro de gracia
        self._mk(tmp_path, "T", "2026-06-04")                   # viejo pero auditado
        out = dias_huerfanos(str(tmp_path), gracia_dias=2, now=now)
        assert [os.path.basename(p) for p in out] == ["2026-06-05"]


class TestHeartbeatEnriquecido:
    """ESPEC §7 (cierre de deuda): tasas de eventos por símbolo y offset NTP
    (chrony) en el latido."""

    def test_parse_chrony_tracking(self):
        from ingestion.main import _parse_chrony_tracking
        linea = ("A29FC87B,162.159.200.123,3,1765574400.123,-0.000012345,"
                 "0.000045678,0.000123,0.001,-0.002,0.05,0.001,64.2,Normal")
        assert _parse_chrony_tracking(linea) == -0.000012345
        assert _parse_chrony_tracking("basura") is None
        assert _parse_chrony_tracking("a,b,c,d,no-num,f,g,h") is None

    def test_rates_line_por_simbolo(self):
        from ingestion.main import _rates_line
        counters = {"AVAXUSDT:depth": 1200, "AVAXUSDT:trades": 60,
                    "LINKUSDT:depth": 600, "LINKUSDT:trades": 0}
        prev = {"AVAXUSDT:depth": 600, "AVAXUSDT:trades": 30}
        assert _rates_line(counters, prev, dt_s=60) == \
            "AVAXUSDT 600d/30t LINKUSDT 600d/0t"
        assert _rates_line(counters, prev, dt_s=0) == ""

    def test_heartbeat_loguea_tasas_y_ntp(self, caplog, monkeypatch):
        import asyncio
        import logging
        import time as treal
        from ingestion import main as m
        monkeypatch.setattr(m, "HEARTBEAT_SECS", 0.03)
        counters = {"X:depth": 0, "X:trades": 0}
        last_seen = {"X:depth": treal.monotonic()}
        stop = asyncio.Event()

        async def run():
            task = asyncio.create_task(
                m.heartbeat(last_seen, stop, counters=counters))
            counters["X:depth"] = 30          # llegan eventos entre latidos
            await asyncio.sleep(0.12)
            stop.set()
            await task

        with caplog.at_level(logging.INFO, logger="main"):
            asyncio.run(asyncio.wait_for(run(), 10))
        assert "tasas/min" in caplog.text
        assert "ntp_offset=" in caplog.text   # en Windows dev: "n/a"
        assert "X " in caplog.text and "d/" in caplog.text


class TestSignals:
    """SETUP_CODE item 10: señales solo si la plataforma lo soporta; en Windows
    la instalación devuelve False y la parada es Ctrl+C (KeyboardInterrupt)."""

    def test_fallback_si_no_soportado(self):
        import asyncio
        from ingestion.main import _install_signal_handlers
        class LoopSinSoporte:
            def add_signal_handler(self, *a): raise NotImplementedError
        assert _install_signal_handlers(LoopSinSoporte(), asyncio.Event()) is False

    def test_instala_si_soportado(self):
        import asyncio
        import signal as sg
        from ingestion.main import _install_signal_handlers
        registrados = []
        class LoopConSoporte:
            def add_signal_handler(self, s, cb): registrados.append(s)
        assert _install_signal_handlers(LoopConSoporte(), asyncio.Event()) is True
        assert set(registrados) == {sg.SIGINT, sg.SIGTERM}
