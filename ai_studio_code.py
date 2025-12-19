import asyncio
import random
from playwright.async_api import async_playwright

URL = "https://gomo666d.github.io/1minsurvivor/"
PLAYER_NAME = f"AlphaGo_Driver_{random.randint(100, 999)}"

async def run_strategic_ai():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 540, "height": 960})
        page = await context.new_page()

        print(f"🚀 启动战略级 AI: {URL}")
        await page.goto(URL)
        await page.wait_for_selector("canvas", timeout=60000)

        game_round = 1
        while True:
            print(f"\n🧠 --- 第 {game_round} 局演练开始 ---")
            
            # 1. 盲激活流程
            await asyncio.sleep(2)
            try:
                await page.focus("canvas")
                await page.mouse.click(270, 480)
                await page.mouse.move(270, 400); await page.mouse.down(); await page.mouse.move(270, 600, steps=10); await page.mouse.up()
                await page.keyboard.press("w")
            except: pass

            current_key = "s"
            await page.keyboard.down(current_key)
            print("🛡️ AI 决策模型已加载：[物品贪婪] [撞击评估] [边界突围]")

            # 2. 实时战斗循环
            while True:
                # 检查死亡
                if await page.is_visible("#game-over-ui"):
                    await page.keyboard.up(current_key)
                    print(f"💀 战斗结束")
                    break

                # === 核心：AI 评分决策算法 ===
                decision_data = await page.evaluate("""() => {
                    try {
                        const scene = game.scene.scenes[0];
                        if (!scene) return null;

                        // 1. 获取基础数据
                        const p = scene.children.list.find(c => c.texture && c.texture.key === 'playerTex' && c.active);
                        if (!p) return null;
                        
                        // 获取HP (从UI读取，因为全局变量不可靠)
                        let currentHp = 100;
                        const hpTextObj = scene.children.list.find(c => c.type === 'Text' && c.text && c.text.startsWith('x'));
                        if (hpTextObj) currentHp = parseInt(hpTextObj.text.replace('x', '')) || 0;

                        // 获取敌人和掉落物
                        const enemies = scene.children.list.filter(c => c.active && c.texture && (c.texture.key === 'zombie_sheet' || c.texture.key === 'zombie_death'));
                        const items = scene.children.list.filter(c => c.active && (c.dropType || (c.texture && c.texture.key && (c.texture.key.includes('heart') || c.texture.key.includes('powerup') || c.texture.key.includes('gun') || c.texture.key.includes('cannon')))));

                        // 2. 定义四个模拟方向 (预判未来 0.2秒的位置)
                        const moves = [
                            { key: 'w', dx: 0, dy: -200 },
                            { key: 's', dx: 0, dy: 200 },
                            { key: 'a', dx: -200, dy: 0 },
                            { key: 'd', dx: 200, dy: 0 }
                        ];

                        let bestKey = 's';
                        let maxScore = -Infinity;
                        let reason = "";

                        // 3. 对四个方向分别打分
                        for (let m of moves) {
                            let score = 0;
                            const futureX = p.x + m.dx;
                            const futureY = p.y + m.dy;

                            // --- A. 边界评分 (求生本能) ---
                            // 地图 2000x2000, 离墙 200px 是红线
                            if (futureX < 200 || futureX > 1800 || futureY < 200 || futureY > 1800) {
                                score -= 5000; // 撞墙几乎必死，极低分
                            }

                            // --- B. 僵尸威胁评估 (含践踏计算) ---
                            let localThreat = 0;
                            for (let e of enemies) {
                                const dist = Phaser.Math.Distance.Between(futureX, futureY, e.x, e.y);
                                
                                if (dist < 80) { 
                                    // 撞击范围！计算代价
                                    // 规则：撞死僵尸掉5血。
                                    if (currentHp > 20) {
                                        // 血量健康，这只是一个 -300 分的障碍，如果那边有宝物，可以接受撞过去
                                        score -= 300; 
                                    } else {
                                        // 血量危急，撞击 = 死亡
                                        score -= 99999;
                                    }
                                } else if (dist < 400) {
                                    // 警戒范围，保持距离
                                    score -= (1500 / dist);
                                }
                            }

                            // --- C. 物品吸引 (贪婪算法) ---
                            let itemBonus = 0;
                            for (let i of items) {
                                const dist = Phaser.Math.Distance.Between(futureX, futureY, i.x, i.y);
                                if (dist < 500) {
                                    // 距离越近，诱惑越大
                                    // 如果这个方向有宝物，且僵尸不多（Score扣的不多），AI 就会选择冲
                                    itemBonus += (8000 / (dist + 10)); 
                                }
                            }
                            score += itemBonus;

                            // --- D. 辅助策略 (回中与随机性) ---
                            // 稍微偏向地图中心，避免一直贴墙
                            const distCenter = Phaser.Math.Distance.Between(futureX, futureY, 1000, 1000);
                            score -= (distCenter * 0.1); 

                            // 选出最高分
                            if (score > maxScore) {
                                maxScore = score;
                                bestKey = m.key;
                                // 简单的决策解释
                                if (itemBonus > 500) reason = "贪婪";
                                else if (score < -4000) reason = "绝境";
                                else reason = "巡逻";
                            }
                        }

                        return { key: bestKey, hp: currentHp, reason: reason };

                    } catch (e) { return null; }
                }""")

                # 执行决策
                if decision_data:
                    target = decision_data['key']
                    # 打印 AI 心理活动
                    print(f"\r❤️ HP: {decision_data['hp']} | 模式: {decision_data['reason']} | 动作: {target.upper()}   ", end="")
                    
                    if target != current_key:
                        await page.keyboard.up(current_key)
                        await page.keyboard.down(target)
                        current_key = target
                
                await asyncio.sleep(0.1) # 思考频率

            # 3. 结算上传
            print("\n📝 战局复盘与上传...")
            await asyncio.sleep(2)
            try:
                if await page.is_visible("#player-name-input"):
                    if not await page.evaluate("document.querySelector('#player-name-input').disabled"):
                        await page.fill("#player-name-input", PLAYER_NAME)
                        await page.keyboard.press("Enter")
                        await asyncio.sleep(2)
                await page.click("#restart-btn")
                game_round += 1
            except: 
                await page.reload()

if __name__ == "__main__":
    try:
        asyncio.run(run_strategic_ai())
    except KeyboardInterrupt:
        print("\n🛑 停止")