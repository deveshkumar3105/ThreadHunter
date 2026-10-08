// Charts initialization and update functions
let categoryChart = null;
let storeChart = null;

function initDashboardCharts(stats) {
  if (!stats) return;

  // Chart 1: Category Average Discounts
  const catCanvas = document.getElementById('categoryDiscountChart');
  if (catCanvas && stats.category_stats) {
    const labels = stats.category_stats.map(c => c.category);
    const data = stats.category_stats.map(c => c.avg_disc);

    if (categoryChart) {
      categoryChart.destroy();
    }

    const ctx = catCanvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.85)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.35)');

    categoryChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Avg Discount (%)',
          data: data,
          backgroundColor: gradient,
          borderRadius: 8,
          borderWidth: 1,
          borderColor: 'rgba(16, 185, 129, 0.9)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#111827',
            titleColor: '#f9fafb',
            bodyColor: '#10b981',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 12,
            callbacks: {
              label: (context) => ` Average Discount: ${context.raw}% OFF`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 80,
            ticks: {
              color: '#94a3b8',
              callback: (value) => `${value}%`
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.05)'
            }
          },
          x: {
            ticks: { color: '#cbd5e1' },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Chart 2: Store Deal Distribution
  const storeCanvas = document.getElementById('storeDealsChart');
  if (storeCanvas && stats.store_stats) {
    const labels = stats.store_stats.map(s => s.store);
    const data = stats.store_stats.map(s => s.count);

    if (storeChart) {
      storeChart.destroy();
    }

    const ctx = storeCanvas.getContext('2d');
    const colors = [
      '#6366f1', '#10b981', '#f59e0b', '#ec4899', 
      '#8b5cf6', '#06b6d4', '#3b82f6', '#f43f5e'
    ];

    storeChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: colors.slice(0, labels.length),
          borderColor: '#101622',
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#cbd5e1',
              boxWidth: 12,
              padding: 14,
              font: { size: 11 }
            }
          },
          tooltip: {
            backgroundColor: '#111827',
            titleColor: '#f9fafb',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 10,
            callbacks: {
              label: (context) => ` ${context.label}: ${context.raw} active deals`
            }
          }
        }
      }
    });
  }
}

window.initDashboardCharts = initDashboardCharts;
