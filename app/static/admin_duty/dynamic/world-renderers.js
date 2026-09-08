(() => {
    const W = window.ShellForgeWorld;
    const tones = { cyan: "#79a5b6", blue: "#7d96ac", amber: "#b99c72", green: "#90a68c", neutral: "#a0aab2", danger: "#c77e72" };
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
        text(c, object.variant.toUpperCase(), 13, h - 12, 8, tone);
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
        partition: WallRenderer, "wall-panel": WallRenderer, door: DoorRenderer,
    };
    W.ObjectRenderers = { RackRenderer, WorkstationRenderer, MonitoringRenderer, SupportStationRenderer: WorkstationRenderer, TriageRenderer: WorkstationRenderer, WallRenderer, DoorRenderer, DecorationRenderer };
    W.textureObject = (scene, object) => {
        const { width: w, height: h } = object.rect;
        const key = ["prop", object.kind, object.variant, object.tone, w, h].join("-");
        if (!scene.textures.exists(key)) {
            const texture = scene.textures.createCanvas(key, w + 2, h + 2);
            (renderers[object.kind] || DecorationRenderer)(texture.context, w, h, object);
        }
        return key;
    };
    W.drawFloors = (scene, map) => {
        const texture = scene.textures.createCanvas("noc-floor", map.width, map.height);
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
            text(c, { "zone-ops": "SALA OPERACYJNA", "zone-entry": "WEJŚCIE / NOC", "zone-support": "CENTRUM WSPARCIA", "zone-observability": "MONITORING", "zone-data-hall": "SERWEROWNIA" }[zone.id] || zone.label, x + 20, y + 32, 13, "#d4dedf66");
        }
        c.strokeStyle = "#8f9da4"; c.lineWidth = 28; c.strokeRect(20, 20, map.width - 40, map.height - 40);
        c.strokeStyle = "#24313a"; c.lineWidth = 9; c.strokeRect(41, 41, map.width - 82, map.height - 82);
        scene.add.image(0, 0, "noc-floor").setOrigin(0).setDepth(0);
    };
})();
