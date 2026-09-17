(() => {
    const W = window.ShellForgeWorld;
    const tones = { cyan: "#79a5b6", blue: "#7d96ac", amber: "#b99c72", green: "#90a68c", neutral: "#a0aab2", danger: "#c77e72" };
    W.visualProfile = map => map.theme === "datacenter-hall" ? "industrial" : "noc";
    const industrialTones = { cyan: "#91acae", blue: "#85959f", amber: "#c3a164", green: "#98ab91", neutral: "#c2c7c6", danger: "#b57869" };
    const round = (c, x, y, w, h, r, fill, stroke) => {
        c.beginPath(); c.roundRect(x, y, w, h, r);
        if (fill) { c.fillStyle = fill; c.fill(); }
        if (stroke) { c.strokeStyle = stroke; c.lineWidth = 1; c.stroke(); }
    };
    const line = (c, x, y, xx, yy, color, width = 1) => {
        c.strokeStyle = color; c.lineWidth = width; c.beginPath(); c.moveTo(x, y); c.lineTo(xx, yy); c.stroke();
    };
    const text = (c, label, x, y, size = 10, color = "#aab9c4") => {
        c.font = "600 " + size + "px Arial"; c.fillStyle = color; c.fillText(label, x, y);
    };
    function RackRenderer(c, w, h, object) {
        const tone = tones[object.tone];
        const gradient = c.createLinearGradient(0, 0, w, 0);
        gradient.addColorStop(0, "#152028"); gradient.addColorStop(.45, "#2e3c47"); gradient.addColorStop(1, "#131c24");
        round(c, 4, 2, w - 8, h - 8, 5, gradient, "#85929b");
        round(c, 10, 14, w - 25, h - 34, 2, "#101820", "#475761");
        round(c, w - 13, 15, 5, h - 31, 1, "#39464e");
        line(c, 4, h - 8, w - 5, h - 8, "#0a1118", 5);
        for (let slot = 0; slot < 8; slot++) {
            const y = 19 + slot * (h - 43) / 8;
            const empty = object.variant === "spare" && slot > 2;
            round(c, 14, y, w - 36, 12, 1, empty ? "#10171b" : slot % 3 === 0 ? "#51606a" : "#34424d", "#73808a");
            if (empty) continue;
            const ports = ["core", "edge"].includes(object.variant) || slot === 0;
            for (let port = 0; port < (ports ? 7 : 4); port++) {
                if (object.variant === "storage" && slot > 0) round(c, 18 + port * 10, y + 2, 8, 8, 1, "#17252c", "#657078");
                else round(c, 18 + port * 6, y + 3, 4, ports ? 5 : 1, 0, "#0c171d");
            }
            line(c, 15, y + 2, 15, y + 9, "#afb6b9", 2);
            line(c, w - 24, y + 2, w - 24, y + 9, "#afb6b9", 2);
            c.fillStyle = slot % 3 === 0 ? tone : "#79ae92"; c.fillRect(w - 31, y + 4, 2, 2);
        }
        const variantLabel = { core: "RDZEŃ", compute: "OBLICZENIA", prod: "PROD", storage: "DANE", edge: "BRZEG", spare: "ZAPAS" }[object.variant] || object.variant;
        text(c, variantLabel.toUpperCase(), 13, h - 12, 8, tone);
        for (const x of [7, w - 10]) for (const y of [7, h - 13]) { c.fillStyle = "#a1a8ab"; c.beginPath(); c.arc(x, y, 1.2, 0, Math.PI * 2); c.fill(); }
    }
    function WorkstationRenderer(c, w, h, object) {
        const tone = tones[object.tone];
        const gradient = c.createLinearGradient(0, 0, 0, h);
        gradient.addColorStop(0, "#78848b"); gradient.addColorStop(.8, "#515f69"); gradient.addColorStop(1, "#35444f");
        round(c, 2, 5, w - 4, h - 9, 12, gradient, "#a7afb1");
        line(c, 13, h - 10, w - 13, h - 10, "#233039", 4);
        const count = w > 245 ? 3 : 2;
        const sw = Math.min(64, (w - 42) / count - 9);
        for (let i = 0; i < count; i++) {
            const x = 18 + i * (sw + 10);
            round(c, x + sw / 2 - 4, 38, 8, 19, 2, "#283640");
            round(c, x + sw / 2 - 13, 53, 26, 5, 2, "#20303c");
            round(c, x, 9, sw, 38, 3, "#14212a", "#a4afb6");
            round(c, x + 4, 13, sw - 8, 29, 1, "#203b49");
            for (let row = 0; row < 4; row++) line(c, x + 8, 19 + row * 5, x + sw - 12 - (row % 3) * 8, 19 + row * 5, row ? "#51778a" : tone);
        }
        round(c, w * .32, h - 28, w * .29, 15, 3, "#263640", "#92a0a7");
        for (let row = 0; row < 3; row++) for (let key = 0; key < 11; key++) round(c, w * .32 + 4 + key * 5, h - 25 + row * 4, 3, 2, 0, "#75868f");
        round(c, w * .65, h - 27, 10, 15, 4, "#b7babb");
        round(c, w - 20, h - 34, 11, 14, 3, "#d0c9b4");
        text(c, object.variant === "triage" ? "ZDARZENIA / KOLEJKA" : object.variant === "support" ? "DOKUMENTACJA" : "STANOWISKO OPERATORA", 15, h - 3, 7, "#b7c3c9");
    }
    function MonitoringRenderer(c, w, h) {
        round(c, 1, 1, w - 2, h - 5, 5, "#202d38", "#8d9aa5");
        for (let screen = 0; screen < 4; screen++) {
            const sw = (w - 29) / 4, x = 8 + screen * (sw + 4);
            round(c, x, 9, sw, h - 26, 2, "#152b39", "#536a76");
            text(c, ["DOSTĘPNOŚĆ", "USŁUGI", "RUCH", "ZDARZENIA"][screen], x + 8, 23, 8);
            for (let row = 0; row < 3; row++) line(c, x + 7, 38 + row * 17, x + sw - 7, 38 + row * 17, "#274551");
        }
        line(c, 10, h - 8, w - 10, h - 8, "#111b23", 4);
    }
    function WallRenderer(c, w, h, object) {
        round(c, 1, 1, w - 2, h - 2, 2, object.variant === "glass" ? "#4a657080" : "#6c7b85", "#98a9b4");
        if (object.variant === "glass") {
            for (let y = 8; y < h; y += 75) { line(c, 0, y, w, y, "#a6b5bb", 3); line(c, 4, y + 8, w - 4, Math.min(h - 6, y + 52), "#a0bfcc55"); }
        }
        line(c, 2, 2, 2, h, "#c2c8ca", 2); line(c, w - 2, 2, w - 2, h, "#233441", 3);
    }
    function DoorRenderer(c, w, h) {
        round(c, 1, 1, w - 2, h - 2, 2, "#79939b", "#c1c8c8");
        line(c, w / 2, 0, w / 2, h, "#1b3541", 2);
        line(c, w / 2 - 12, 4, w / 2 - 12, h - 4, "#c9cebf", 2);
    }
    function InfrastructureRenderer(c, w, h, object) {
        const tone = tones[object.tone];
        round(c, 2, 2, w - 4, h - 6, 5, "#24313a", "#89969d");
        if (object.kind === "cooling-unit") {
            round(c, 10, 12, w - 20, h * .56, 4, "#17252d", "#667780");
            for (let blade = 0; blade < 6; blade++) {
                c.save(); c.translate(w / 2, h * .31); c.rotate(blade * Math.PI / 3);
                round(c, -3, -h * .19, 6, h * .18, 3, "#718792"); c.restore();
            }
            for (let y = h * .65; y < h - 20; y += 12) line(c, 12, y, w - 12, y, "#53656e");
        } else if (object.kind === "patch-panel") {
            for (let row = 0; row < 2; row++) for (let port = 0; port < 14; port++) {
                round(c, 10 + port * (w - 20) / 14, 10 + row * 13, 7, 7, 1, port % 3 ? "#101a20" : tone, "#68767d");
            }
        } else if (object.kind === "access-panel") {
            round(c, 9, 9, w - 18, h - 24, 3, "#10212a", "#647681");
            c.fillStyle = tone; c.fillRect(w / 2 - 4, 18, 8, 8);
            for (let y = 38; y < h - 18; y += 12) line(c, 15, y, w - 15, y, "#3e5a66");
        } else {
            for (let row = 0; row < 4; row++) {
                round(c, 12, 16 + row * (h - 38) / 4, w - 24, 18, 2, row === 0 ? "#3c4d57" : "#18252d", "#6d7a80");
                c.fillStyle = row < 3 ? tone : "#8b997f"; c.fillRect(w - 27, 23 + row * (h - 38) / 4, 4, 4);
            }
        }
        if (object.label) text(c, object.label, 10, h - 9, 8, tone);
    }
    function DecorationRenderer(c, w, h, object) {
        if (object.kind === "chair") {
            c.fillStyle = "#1c2b35"; c.beginPath(); c.ellipse(w / 2, h / 2, w * .35, h * .32, 0, 0, Math.PI * 2); c.fill();
            round(c, 7, 2, w - 14, 16, 7, "#475965", "#8a989e");
            line(c, 4, 18, 4, h - 9, "#a4adb0", 3); line(c, w - 4, 18, w - 4, h - 9, "#a4adb0", 3);
        } else if (object.kind === "plant") {
            round(c, w * .25, h * .5, w * .5, h * .45, 6, "#b3b1a0", "#dad7c6");
            for (let leaf = 0; leaf < 9; leaf++) {
                c.save(); c.translate(w / 2, h * .45); c.rotate(leaf * 2.3); c.fillStyle = leaf % 2 ? "#547f68" : "#78967c"; c.beginPath(); c.ellipse(0, -10, 5, 17, .3, 0, Math.PI * 2); c.fill(); c.restore();
            }
        } else if (object.kind === "cabinet") {
            round(c, 1, 1, w - 2, h - 5, 4, "#686e6b", "#b6b5a6");
            for (let i = 0; i < 12; i++) round(c, 9 + i * (w - 18) / 12, 9, 9, 30 + i % 3 * 4, 1, ["#718fa0", "#a99979", "#8b9a91"][i % 3]);
            line(c, 2, h - 19, w - 2, h - 19, "#25353f", 4);
            for (let i = 0; i < 3; i++) round(c, 6 + i * w / 3, h - 15, w / 3 - 13, 10, 1, "#a1aaa9");
        } else if (object.kind === "board") {
            round(c, 0, 0, w, h, 4, "#394f5c", "#a0acb2");
            text(c, "TRIAGE / ZDARZENIA", 10, 16, 9);
            for (let i = 0; i < 5; i++) round(c, 10 + i * (w - 20) / 5, 25, (w - 30) / 5 - 5, 22, 2, ["#88969b", "#998e76", "#607f89"][i % 3]);
        } else {
            round(c, 0, 0, w, h, 2, tones[object.tone] + "66");
        }
    }
    const renderers = {
        "server-rack": RackRenderer, "operator-desk": WorkstationRenderer, "monitor-wall": MonitoringRenderer,
        "network-rack": RackRenderer, "patch-panel": InfrastructureRenderer, "ups-unit": InfrastructureRenderer,
        "cooling-unit": InfrastructureRenderer, "access-panel": InfrastructureRenderer,
        partition: WallRenderer, "wall-panel": WallRenderer, door: DoorRenderer,
    };
    W.ObjectRenderers = { RackRenderer, WorkstationRenderer, MonitoringRenderer, SupportStationRenderer: WorkstationRenderer, TriageRenderer: WorkstationRenderer, WallRenderer, DoorRenderer, DecorationRenderer };
    function IndustrialRenderer(c, w, h, object) {
        const accent = industrialTones[object.tone];
        if (object.kind === "cabinet" && object.variant === "maintenance-cart") {
            for (const x of [9, w - 21]) round(c, x, h - 11, 12, 10, 3, "#151c1d", "#747c77");
            round(c, 7, 7, w - 21, h - 17, 2, "#626b61", "#9da494");
            round(c, 12, 11, w - 31, 17, 1, "#222c2c", "#929c8d");
            line(c, 10, 34, w - 19, 34, "#283331", 2);
            line(c, w * .4, 39, w * .65, 39, "#b4bbaa", 3);
            line(c, w - 9, 8, w - 9, h - 17, "#a0a999", 3);
            line(c, w - 15, 8, w - 4, 8, "#a0a999", 3);
            round(c, 17, 15, 24, 8, 1, "#a58e61");
            for (let x = 49; x < w - 30; x += 10) line(c, x, 15, x + 4, 24, "#b4b9a7", 3);
            return;
        }
        if (object.kind === "cabinet" && object.variant === "service-crate") {
            round(c, 2, 2, w - 4, h - 4, 2, "#655f4d", "#a69e83");
            round(c, 7, 6, w - 14, h - 15, 1, "#81785e", "#3c4038");
            for (const x of [16, w - 22]) {
                round(c, x, 2, 6, h - 4, 0, "#424b46", "#9fa78d");
                round(c, x - 1, h - 14, 8, 7, 1, "#bec0a4");
            }
            round(c, w / 2 - 12, 4, 24, 5, 1, "#27332f");
            text(c, "CZĘŚCI", 29, h / 2 + 5, 7, "#e0d7b6");
            return;
        }
        if (object.kind === "wall-panel" && object.variant === "fiber-frame") {
            for (const x of [3, w - 7]) round(c, x, 2, 4, h - 4, 0, "#84918c", "#202a2b");
            for (const y of [8, h - 10]) line(c, 4, y, w - 4, y, "#9ca69a", 3);
            round(c, 10, 12, w - 20, 20, 1, "#394844", "#97a48f");
            for (let p = 0; p < 6; p++) {
                const x = 15 + p * (w - 28) / 6;
                round(c, x, 17, 4, 8, 0, "#acc1a0", "#182825");
                c.strokeStyle = p % 2 ? "#ad9862" : "#93acaa"; c.lineWidth = 1.5;
                c.beginPath(); c.moveTo(x + 2, 26); c.bezierCurveTo(x - 8, 48, w - x, 65, w / 2 + p * 2, h - 14); c.stroke();
            }
            round(c, 15, h - 17, w - 30, 8, 1, "#465750");
            return;
        }
        if (object.kind === "wall-panel" && object.variant === "power-distribution") {
            round(c, 1, 1, w - 2, h - 3, 1, "#737967", "#a3aa95");
            round(c, 7, 7, w - 14, h - 18, 1, "#283430", "#969f87");
            for (let x = 14; x < w - 32; x += 19) {
                round(c, x, 12, 12, 19, 1, "#a5ac95", "#152520");
                round(c, x + 4, 17, 4, 9, 0, "#26392e");
            }
            c.fillStyle = "#ccb271"; c.beginPath(); c.moveTo(w - 24, 13); c.lineTo(w - 15, 28); c.lineTo(w - 33, 28); c.closePath(); c.fill();
            text(c, "!", w - 26, 25, 11, "#26352e");
            text(c, "ROZDZIAŁ ZASILANIA", 12, h - 6, 8, "#dde0c6");
            return;
        }
        const rack = ["server-rack", "network-rack"].includes(object.kind);
        if (rack) {
            round(c, 1, 1, w - 2, h - 2, 1, "#151a1c", "#8c9292");
            round(c, 6, 6, w - 17, h - 14, 0, "#393f41", "#505858");
            round(c, 11, 17, w - 27, h - 36, 0, "#0e1315");
            c.fillStyle = "#575f60"; c.fillRect(w - 10, 5, 5, h - 10);
            line(c, 4, h - 4, w - 3, h - 4, "#080c0d", 5);
            const network = object.kind === "network-rack";
            const storage = object.variant === "storage";
            const rows = network ? 6 : storage ? 5 : 8;
            const slotHeight = (h - 40) / rows;
            for (let row = 0; row < rows; row++) {
                const y = 20 + row * slotHeight;
                const empty = object.variant === "spare" && row > 2;
                round(c, 14, y, w - 34, slotHeight - 4, 0, empty ? "#14191b" : row % 2 ? "#333a3c" : "#485052", "#626a6a");
                if (empty) continue;
                if (network || storage) {
                    const count = network ? 6 : 4;
                    const unit = (w - 44) / count;
                    for (let p = 0; p < count; p++) {
                        round(c, 18 + p * unit, y + 3, unit - 3, slotHeight - 10, 0, "#171d1f", "#818984");
                        if (storage) line(c, 19 + p * unit, y + 5, 19 + p * unit, y + slotHeight - 10, "#969a8d", 2);
                    }
                } else {
                    for (let x = 21; x < w - 33; x += 4) line(c, x, y + 3, x, y + slotHeight - 7, "#171d20");
                }
                c.fillStyle = accent; c.fillRect(w - 25, y + 3, 2, 2);
            }
            for (const x of [8, w - 8]) for (let y = 10; y < h - 10; y += 22) {
                c.fillStyle = "#a1a6a2"; c.fillRect(x, y, 2, 2);
            }
            const label = { compute: "CPU", prod: "USŁUGI", storage: "DYSKI", spare: "REZERWA", core: "RDZEŃ", edge: "BRZEG" }[object.variant];
            text(c, label || "SERWER", 14, 12, 7, "#d0d1c7");
            text(c, object.id.split("-").pop().toUpperCase(), 14, h - 7, 8, accent);
            return;
        }
        if (["floor-marking", "light-strip", "cable-tray"].includes(object.kind)) {
            const vertical = h > w;
            if (object.kind === "light-strip") {
                round(c, 0, 0, w, h, 0, "#31393a", "#596261");
                round(c, 2, 2, w - 4, h - 4, 0, "#d4dbd4");
            } else if (object.kind === "cable-tray") {
                round(c, 0, 0, w, h, 0, "#202728", "#727978");
                for (let p = 3; p < (vertical ? w : h) - 2; p += 3) line(c, vertical ? p : 0, vertical ? 0 : p, vertical ? p : w, vertical ? h : p, p % 2 ? "#606b67" : "#8c8069");
                for (let p = 8; p < (vertical ? h : w); p += 24) line(c, vertical ? 0 : p, vertical ? p : 0, vertical ? w : p, vertical ? p : h, "#a0a39a", 2);
            } else if (w > 35 && h > 100) {
                c.fillStyle = object.tone === "cyan" ? "#829b9820" : "#b99b6720"; c.fillRect(0, 0, w, h);
                for (const x of [3, w - 4]) line(c, x, 0, x, h, accent, 2);
                for (let y = 30; y < h; y += 120) {
                    line(c, w / 2 - 9, y + 8, w / 2, y, accent, 2); line(c, w / 2, y, w / 2 + 9, y + 8, accent, 2);
                }
                c.save(); c.translate(w / 2 + 3, h - 30); c.rotate(-Math.PI / 2);
                text(c, object.tone === "cyan" ? "ZIMNA ALEJKA" : "CIEPŁA ALEJKA", 0, 0, 10, accent); c.restore();
            } else {
                c.fillStyle = accent; c.fillRect(0, 0, w, h);
                for (let p = 0; p < w; p += 24) line(c, p, h, p + h, 0, "#303534", 6);
            }
            return;
        }
        if (["partition", "wall-panel", "door"].includes(object.kind)) {
            round(c, 0, 0, w, h, 0, "#454d4d", "#a1a59d");
            line(c, w - 3, 0, w - 3, h, "#161d1e", 4);
            for (let y = 10; y < h; y += 30) line(c, 3, y, w - 4, y, "#232b2b", 2);
            return;
        }
        if (object.kind === "operator-desk" || object.kind === "monitor-wall") {
            round(c, 1, 1, w - 2, h - 3, 1, "#495151", "#a0a59f");
            round(c, 5, 5, w - 10, h - 14, 0, "#262d2e", "#151b1d");
            const count = object.kind === "monitor-wall" ? 4 : 3;
            const sw = (w - 25) / count;
            for (let i = 0; i < count; i++) {
                const x = 10 + i * sw;
                round(c, x, 10, sw - 6, h - 34, 0, "#101b1e", "#727e7c");
                text(c, ["STAN", "USŁUGI", "RUCH", "ALERTY"][i], x + 4, 21, 7, "#a5bcb8");
                if (object.kind !== "monitor-wall") for (let y = 30; y < h - 35; y += 7) line(c, x + 6, y, x + sw - 16 - (y % 3) * 5, y, "#647e7a");
            }
            if (object.kind === "operator-desk") {
                for (let x = 16; x < w * .65; x += 8) round(c, x, h - 20, 5, 5, 0, "#92978c");
                text(c, "KONSOLA / DC", w - 87, h - 13, 8, "#c4c6b9");
            }
            return;
        }
        if (["cooling-unit", "ups-unit", "patch-panel", "access-panel"].includes(object.kind)) {
            round(c, 1, 1, w - 2, h - 3, 1, "#535b59", "#a1a69e");
            round(c, 7, 7, w - 18, h - 19, 0, "#303839", "#151c1d");
            line(c, w - 7, 4, w - 7, h - 5, "#79827c", 4);
            if (object.kind === "cooling-unit") {
                c.fillStyle = "#121d20"; c.beginPath(); c.arc(w / 2, h * .31, w * .36, 0, Math.PI * 2); c.fill();
                c.strokeStyle = "#7e8f8c"; c.lineWidth = 3; c.stroke();
                for (let y = h * .56; y < h - 30; y += 7) line(c, 15, y, w - 22, y, "#111c1e", 3);
                text(c, "CHŁODZENIE", 14, h - 13, 8, "#b3c7c2");
            } else if (object.kind === "patch-panel") {
                for (let row = 0; row < 2; row++) for (let port = 0; port < 12; port++) round(c, 13 + port * (w - 28) / 12, 10 + row * 12, 7, 7, 0, "#10191b", "#9ba394");
            } else {
                round(c, 13, 13, w - 35, Math.min(30, h * .25), 0, "#142322", "#788d81");
                for (let x = 17; x < w - 28; x += 7) line(c, x, 23, x, 30, accent, 3);
                for (let y = h * .44; y < h - 22; y += 12) line(c, 14, y, w - 24, y, "#152021", 4);
                if (w > 70) text(c, object.kind === "ups-unit" ? "ZASILANIE / UPS" : "STAN", 12, h - 10, 8, accent);
            }
            for (const x of [4, w - 5]) for (const y of [5, h - 8]) { c.fillStyle = "#c1c0ae"; c.fillRect(x, y, 2, 2); }
            return;
        }
        DecorationRenderer(c, w, h, object);
    }
    function industrialFloor(scene, map) {
        const texture = scene.textures.createCanvas("industrial-floor-" + (map.world_id || map.id), map.width, map.height);
        const c = texture.context;
        c.fillStyle = "#343b3c"; c.fillRect(0, 0, map.width, map.height);
        const floors = ["#626a67", "#535e5f", "#48575a", "#575e59", "#62635a"];
        const sectors = ["zone-operations-entry", "zone-compute-hall", "zone-network-core", "zone-storage-services", "zone-power-cooling"];
        map.objects.filter(o => o.kind === "floor-zone").forEach(zone => {
            const index = Math.max(0, sectors.indexOf(zone.id));
            const { x, y, width: w, height: h } = zone.rect;
            c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
            c.fillStyle = floors[index]; c.fillRect(x, y, w, h);
            for (let xx = x; xx < x + w; xx += 60) for (let yy = y; yy < y + h; yy += 60) {
                round(c, xx + 1, yy + 1, 58, 58, 0, null, "#242e2e");
                line(c, xx + 3, yy + 3, xx + 56, yy + 3, "#a2aaa230");
                c.fillStyle = "#bac0b655"; c.fillRect(xx + 6, yy + 6, 2, 2); c.fillRect(xx + 52, yy + 52, 2, 2);
                if ((index === 1 && ((xx - x) / 60) % 3 === 0) || index === 4) {
                    for (let p = 12; p < 50; p += 6) line(c, xx + 13, yy + p, xx + 46, yy + p, "#242e2e80", 2);
                }
            }
            c.strokeStyle = index === 4 ? "#b99f65" : "#b1b6a8"; c.lineWidth = 2; c.strokeRect(x + 10, y + 10, w - 20, h - 20);
            const sign = scene.textures.createCanvas("dc-sector-" + zone.id, Math.min(w - 30, 345), 30);
            round(sign.context, 0, 0, sign.width, 30, 0, "#202a2b", "#858e80");
            text(sign.context, String.fromCharCode(65 + index) + " / " + zone.label, 9, 20, 12, "#d4d5c7");
            scene.add.image(x + 15, y + 14, sign.key).setOrigin(0).setDepth(2.2);
            if (index === 1) for (let row = 0; row < 3; row++) text(c, "RZĄD " + (row + 1).toString().padStart(2, "0"), x + 20, y + 270 + row * 240, 13, "#c1c5b8");
            if (index === 4) for (let xx = x + 25; xx < x + w - 30; xx += 26) line(c, xx, y + h - 20, xx + 12, y + h - 10, "#c6a45f", 5);
            if (index === 0) {
                text(c, "DC / HALA INFRASTRUKTURY", x + 45, y + h - 85, 19, "#ced0c1");
                text(c, "KONTROLA DOSTĘPU  /  STREFA TECHNICZNA", x + 45, y + h - 62, 10, "#b0b9b0");
                line(c, x + 345, y + 190, x + 345, y + 150, "#b0b9b0", 2);
                line(c, x + 337, y + 160, x + 345, y + 150, "#b0b9b0", 2);
                line(c, x + 353, y + 160, x + 345, y + 150, "#b0b9b0", 2);
                text(c, "HALA", x + 330, y + 140, 10, "#b0b9b0");
            }
            if (index === 2) {
                line(c, x + 346, y + 158, x + 346, y + 268, "#98ab9170", 2);
                text(c, "F01 / ŚWIATŁOWÓD", x + 355, y + 220, 8, "#b0b9b0");
            }
            if (index === 4) {
                text(c, "PRZEPŁYW POWIETRZA", x + 220, y + 345, 9, "#b0b9b0");
                for (const dx of [195, 365]) {
                    line(c, x + dx, y + 365, x + dx, y + 395, "#91acae90", 2);
                    line(c, x + dx - 6, y + 387, x + dx, y + 395, "#91acae90", 2);
                    line(c, x + dx + 6, y + 387, x + dx, y + 395, "#91acae90", 2);
                }
            }
            c.restore();
        });
        c.strokeStyle = "#7b827d"; c.lineWidth = 28; c.strokeRect(20, 20, map.width - 40, map.height - 40);
        c.strokeStyle = "#151e20"; c.lineWidth = 8; c.strokeRect(41, 41, map.width - 82, map.height - 82);
        scene.add.image(0, 0, texture.key).setOrigin(0).setDepth(0);
    }
    W.textureObject = (scene, object, profile = "noc") => {
        const { width: w, height: h } = object.rect;
        const rackLabel = profile === "industrial" && ["server-rack", "network-rack"].includes(object.kind) ? object.id.split("-").pop() : "";
        const label = profile === "noc" && ["cooling-unit", "ups-unit", "patch-panel", "access-panel"].includes(object.kind) ? object.label || "" : "";
        const key = ["prop", profile, object.kind, object.variant, object.tone, w, h, label, rackLabel].join("-");
        if (!scene.textures.exists(key)) {
            const texture = scene.textures.createCanvas(key, w + 2, h + 2);
            (profile === "industrial" ? IndustrialRenderer : renderers[object.kind] || DecorationRenderer)(texture.context, w, h, object);
        }
        return key;
    };
    W.drawFloors = (scene, map) => {
        if (W.visualProfile(map) === "industrial") return industrialFloor(scene, map);
        const floorKey = "world-floor-" + (map.world_id || map.id);
        const texture = scene.textures.createCanvas(floorKey, map.width, map.height);
        const c = texture.context;
        c.fillStyle = "#34434b"; c.fillRect(0, 0, map.width, map.height);
        for (const zone of map.objects.filter(o => o.kind === "floor-zone")) {
            const { x, y, width: w, height: h } = zone.rect;
            c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
            c.fillStyle = { carpet: "#3c4c55", raised: "#738087", wood: "#797c73", stone: "#596970" }[zone.variant];
            c.fillRect(x, y, w, h);
            if (zone.variant === "raised") {
                for (let xx = x; xx < x + w; xx += 48) for (let yy = y; yy < y + h; yy += 48) {
                    round(c, xx + 1, yy + 1, 45, 45, 1, "#849095", "#535f67");
                    c.fillStyle = "#58676c"; c.fillRect(xx + 5, yy + 5, 2, 2);
                }
            } else if (zone.variant === "wood") {
                for (let yy = y; yy < y + h; yy += 22) { line(c, x, yy, x + w, yy, "#464f4922"); for (let xx = x + (yy % 44 ? 64 : 0); xx < x + w; xx += 128) line(c, xx, yy, xx, yy + 22, "#343f4422"); }
            } else if (zone.variant === "carpet") {
                for (let yy = y; yy < y + h; yy += 5) for (let xx = x + yy % 11; xx < x + w; xx += 9) line(c, xx, yy, xx + 3, yy + 1, "#80919916");
                for (let yy = y + 90; yy < y + h; yy += 90) line(c, x, yy, x + w, yy, "#1e303322");
            } else {
                for (let yy = y; yy < y + h; yy += 90) line(c, x, yy, x + w, yy, "#91a3aa25");
            }
            c.restore();
            c.strokeStyle = "#b4c1c333"; c.lineWidth = 4; c.strokeRect(x + 3, y + 3, w - 6, h - 6);
            text(c, zone.label, x + 20, y + 32, 13, "#d4dedf66");
        }
        c.strokeStyle = "#8f9da4"; c.lineWidth = 28; c.strokeRect(20, 20, map.width - 40, map.height - 40);
        c.strokeStyle = "#24313a"; c.lineWidth = 9; c.strokeRect(41, 41, map.width - 82, map.height - 82);
        scene.add.image(0, 0, floorKey).setOrigin(0).setDepth(0);
    };
})();
