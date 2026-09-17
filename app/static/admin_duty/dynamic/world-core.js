(() => {
    const W = window.ShellForgeWorld = {};
    W.MapLoader = class MapLoader {
        static load(data) {
            if (!data || !Number.isFinite(data.width) || !Number.isFinite(data.height) || data.width <= 0 || data.height <= 0) throw new Error("Nieprawidłowe wymiary mapy.");
            for (const field of ["objects", "interactions", "collision_zones", "sectors"]) {
                if (!Array.isArray(data[field])) throw new Error("Brak danych mapy: " + field);
            }
            const ids = new Set();
            for (const item of data.objects) {
                const r = item.rect;
                if (ids.has(item.id) || !r || ![r.x, r.y, r.width, r.height].every(Number.isFinite) || r.x < 0 || r.y < 0 || r.width <= 0 || r.height <= 0 || r.x + r.width > data.width || r.y + r.height > data.height) throw new Error("Nieprawidłowy obiekt mapy.");
                ids.add(item.id);
            }
            const pointValid = p => p && [p.x, p.y].every(Number.isFinite) && p.x >= 0 && p.y >= 0 && p.x <= data.width && p.y <= data.height;
            if (!pointValid(data.player_spawn)) throw new Error("Nieprawidłowy spawn.");
            const interactionIds = new Set();
            for (const item of data.interactions) {
                if (interactionIds.has(item.id) || !pointValid(item.position) || !Number.isFinite(item.radius) || item.radius <= 0 || (item.object_id && !ids.has(item.object_id))) throw new Error("Nieprawidłowa interakcja.");
                interactionIds.add(item.id);
            }
            const sectorIds = new Set();
            for (const item of data.sectors) {
                const r = item.rect;
                if (sectorIds.has(item.id) || !r || ![r.x, r.y, r.width, r.height].every(Number.isFinite) || r.x < 0 || r.y < 0 || r.width <= 0 || r.height <= 0 || r.x + r.width > data.width || r.y + r.height > data.height) throw new Error("Nieprawidłowy sektor mapy.");
                sectorIds.add(item.id);
            }
            return data;
        }
    };
    W.RuntimeBridge = class RuntimeBridge {
        constructor(monitoring) { this.update(monitoring); }
        update(monitoring) {
            this.signals = new Map((monitoring?.signals || []).map(s => [s.resource_id, s]));
        }
        severity(resource) { return this.signals.get(resource)?.severity || "ok"; }
        color(resource) { return { ok: 0x61b49a, warning: 0xd4a15c, critical: 0xd86e66 }[this.severity(resource)]; }
    };
    W.CameraController = class CameraController {
        constructor(scene, player, map) {
            this.scene = scene;
            this.player = player;
            this.map = map;
            this.resize();
        }
        resize() {
            const camera = this.scene.cameras.main;
            camera.setBounds(0, 0, this.map.width, this.map.height);
            camera.setZoom(Math.max(0.88, Math.min(1.08, camera.height / 760)));
            camera.startFollow(this.player, false, 0.075, 0.075);
        }
    };
    W.nearestInteraction = (items, position) => {
        let nearest = null;
        let closest = Infinity;
        for (const item of items) {
            const distance = Math.hypot(position.x - item.position.x, position.y - item.position.y);
            if (distance <= item.radius && distance < closest) { nearest = item; closest = distance; }
        }
        return nearest;
    };
    W.DiscoveryState = class DiscoveryState {
        constructor(map) { this.map = map; this.discovered = new Set(); }
        visit(x, y) {
            const sector = this.map.sectors.find(({ rect: r }) => x >= r.x && y >= r.y && x <= r.x + r.width && y <= r.y + r.height) || null;
            const fresh = sector && !this.discovered.has(sector.id);
            if (sector) this.discovered.add(sector.id);
            return { current: sector, newlyDiscovered: Boolean(fresh), discovered: this.discovered.size, total: this.map.sectors.length };
        }
    };
})();
