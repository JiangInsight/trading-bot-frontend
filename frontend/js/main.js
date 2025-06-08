const API_BASE_URL = 'https://你的阿里云服务器IP:5000';

async function fetchData() {
    try {
        // 获取账户信息
        const accountResponse = await fetch(`${API_BASE_URL}/account_info`);
        const accountData = await accountResponse.json();
        
        document.getElementById('usdtBalance').textContent = accountData.usdt_holding.toFixed(2);
        document.getElementById('holding').textContent = accountData.holding.toFixed(8);
        document.getElementById('totalValue').textContent = accountData.account_total.toFixed(2);

        // 获取市场数据
        const marketResponse = await fetch(`${API_BASE_URL}/market_data`);
        const marketData = await marketResponse.json();
        
        document.getElementById('currentPrice').textContent = marketData.price.toFixed(2);
        const priceChangeElement = document.getElementById('priceChange');
        priceChangeElement.textContent = `${marketData.price_change_percent.toFixed(2)}%`;
        priceChangeElement.className = marketData.price_change_percent >= 0 ? 'positive-change' : 'negative-change';
        document.getElementById('volume').textContent = marketData.volume.toFixed(2);

        // 获取最近交易
        const tradesResponse = await fetch(`${API_BASE_URL}/recent_trades`);
        const tradesData = await tradesResponse.json();
        
        const tradesTable = document.getElementById('tradesTable');
        tradesTable.innerHTML = '';
        
        tradesData.forEach(trade => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(trade.timestamp * 1000).toLocaleString()}</td>
                <td>${trade.action}</td>
                <td>${trade.price.toFixed(2)}</td>
                <td>${trade.quantity.toFixed(8)}</td>
                <td>${trade.value.toFixed(2)}</td>
            `;
            tradesTable.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// 每5秒更新一次数据
setInterval(fetchData, 5000);
// 初始加载
fetchData(); 