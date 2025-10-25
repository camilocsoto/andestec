import ApexCharts from 'apexcharts';
// extract the data from the array
const dataContainer = document.getElementById('data-container-charts');

let chartsData = {};
try {
  chartsData = JSON.parse(dataContainer?.getAttribute('data-charts') || '{}');
} catch (e) {
  console.error('[charts] JSON inválido en data-charts:', e);
  chartsData = { labels: [], series: {} };
}

// Normaliza accesos
const labels = chartsData.labels || [];
const series = chartsData.series || {};
const serieExtracted = series.porc_masa_gas_extracted || []; // current capacity chart
const serieRemovedKg = series.masa_remov_kg || []; // visitors chart


const getMainChartOptions = (chartsData) => {
  let mainChartColors = {};
  if (document.documentElement.classList.contains('dark')) {
    mainChartColors = {
      borderColor: '#374151',
      labelColor: '#9CA3AF',
      opacityFrom: 0,
      opacityTo: 0.15,
    };
  } else {
    mainChartColors = {
      borderColor: '#F3F4F6',
      labelColor: '#6B7280',
      opacityFrom: 0.45,
      opacityTo: 0,
    };
  }

  // ✅ Accesos seguros (por si viene vacío)
  const labels = chartsData?.labels ?? [];
  const series = chartsData?.series ?? {};
  const sRestant   = series?.porc_masa_gas_restant   ?? [];
  const sExtracted = series?.porc_masa_gas_extracted ?? [];

  return {
    chart: {
      height: 420,
      type: 'area',
      fontFamily: 'Inter, sans-serif',
      foreColor: mainChartColors.labelColor,
      toolbar: { show: false },
    },
    fill: {
      type: 'gradient',
      gradient: {
        enabled: true,
        opacityFrom: mainChartColors.opacityFrom,
        opacityTo: mainChartColors.opacityTo,
      },
    },
    dataLabels: { enabled: false },
    tooltip: {
      style: { fontSize: '14px', fontFamily: 'Inter, sans-serif' },
      y: { formatter: (v) => (v == null ? '--' : `${v}%`) }, // ambas series en %
    },
    grid: {
      show: true,
      borderColor: mainChartColors.borderColor,
      strokeDashArray: 1,
      padding: { left: 35, bottom: 15 },
    },
    series: [
      {
        name: 'Gas restante (%)',
        data: sRestant,
        color: '#1A56DB',
      },
      {
        name: 'Gas utilizado (%)',
        data: sExtracted,
        color: '#00b8ff',
      },
    ],
    markers: {
      size: 5,
      strokeColors: '#ffffff',
      hover: { sizeOffset: 3 },
    },
    xaxis: {
      categories: labels, // timestamps ISO8601
      labels: {
        rotate: -15,
        style: {
          colors: [mainChartColors.labelColor],
          fontSize: '12px',
          fontWeight: 500,
        },
      },
      axisBorder: { color: mainChartColors.borderColor },
      axisTicks: { color: mainChartColors.borderColor },
      crosshairs: {
        show: true,
        position: 'back',
        stroke: { color: mainChartColors.borderColor, width: 1, dashArray: 10 },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: [mainChartColors.labelColor],
          fontSize: '14px',
          fontWeight: 500,
        },
        formatter: (value) => (value == null ? '--' : `${value}%`),
      },
      tickAmount: 10,
      min: 0,
      max: 100,
      forceNiceScale: true,
    },
    legend: {
      fontSize: '14px',
      fontWeight: 500,
      fontFamily: 'Inter, sans-serif',
      labels: { colors: [mainChartColors.labelColor] },
      itemMargin: { horizontal: 10 },
    },
    responsive: [
      { breakpoint: 1024, options: { xaxis: { labels: { show: false } } } },
    ],
  };
};

// Envoltura principal
window.addEventListener('load', function () {
  const dataContainer = document.getElementById('data-container-charts');
  if (!dataContainer) return;

  let chartsData = {};
  try {
    chartsData = JSON.parse(dataContainer.getAttribute('data-charts') || '{}');
  } catch (e) {
    console.error('[main-chart] JSON inválido:', e);
    chartsData = {};
  }

  const mainEl = document.getElementById('main-chart');
  if (mainEl) {
    const options = getMainChartOptions(chartsData);
    const chart = new ApexCharts(mainEl, options);
    chart.render();

    document.addEventListener('dark-mode', function () {
      chart.updateOptions(getMainChartOptions(chartsData));
    });
  }
});


// chart for extracted capacity of gas
if (document.getElementById('new-products-chart')) {
  // Empaqueta como [{x, y}] con timestamps en X y % extraído en Y
  const capacitySerie = labels.map((time, idx) => ({
    x: time,
    y: (idx < serieExtracted.length ? serieExtracted[idx] : null),
  }));

  const options = {
    colors: ['#1A56DB'],
    series: [
      {
        name: 'Gas utilizado (%)',
        color: '#1A56DB',
        data: capacitySerie,
      }
    ],
    chart: {
      type: 'bar',
      height: '140px',
      fontFamily: 'Inter, sans-serif',
      foreColor: '#4B5563',
      toolbar: { show: false },
    },
    plotOptions: {
      bar: {
        columnWidth: '90%',
        borderRadius: 3,
      }
    },
    tooltip: {
      shared: false,
      intersect: false,
      style: { fontSize: '14px', fontFamily: 'Inter, sans-serif' },
      y: { formatter: (v) => (v == null ? '--' : `${v}%`) },
    },
    states: {
      hover: { filter: { type: 'darken', value: 1 } }
    },
    stroke: { show: true, width: 5, colors: ['transparent'] },
    grid: { show: false },
    dataLabels: { enabled: false },
    legend: { show: false },
    xaxis: {
      type: 'category',
      categories: labels,
      floating: false,
      labels: { show: false },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: { labels: false },
    fill: { opacity: 1 },
  };

  const chart = new ApexCharts(document.getElementById('new-products-chart'), options);
  chart.render();

  // Dark mode re-render
  document.addEventListener('dark-mode', function () {
    chart.updateOptions(options);
  });
}

// chart to show kg of gas removed
const getVisitorsChartOptions = () => {
  let visitorsChartColors = {};
  if (document.documentElement.classList.contains('dark')) {
    visitorsChartColors = { fillGradientShade: 'dark', fillGradientShadeIntensity: 0.45 };
  } else {
    visitorsChartColors = { fillGradientShade: 'light', fillGradientShadeIntensity: 1 };
  }

  return {
    series: [{
      name: 'Gas removido (kg)',
      data: serieRemovedKg,
    }],
    labels: labels,
    chart: {
      type: 'area',
      height: '305px',
      fontFamily: 'Inter, sans-serif',
      sparkline: { enabled: true },
      toolbar: { show: false },
    },
    fill: {
      type: 'gradient',
      gradient: {
        shade: visitorsChartColors.fillGradientShade,
        shadeIntensity: visitorsChartColors.fillGradientShadeIntensity,
      },
    },
    plotOptions: { area: { fillTo: 'end' } },
    theme: { monochrome: { enabled: true, color: '#1A56DB' } },
    tooltip: {
      style: { fontSize: '14px', fontFamily: 'Inter, sans-serif' },
      y: { formatter: (v) => (v == null ? '--' : `${v}`) },
    },
  };
};

// WEEK SIGNUPS CHART (barras)
const getSignupsChartOptions = () => {
  let signupsChartColors = {};
  if (document.documentElement.classList.contains('dark')) {
    signupsChartColors = { backgroundBarColors: ['#374151','#374151','#374151','#374151','#374151','#374151','#374151'] };
  } else {
    signupsChartColors = { backgroundBarColors: ['#E5E7EB','#E5E7EB','#E5E7EB','#E5E7EB','#E5E7EB','#E5E7EB','#E5E7EB'] };
  }

  return {
    series: [{
      name: 'Internal pressure of gas',
      data: serieRemovedKg,
    }],
    labels: labels,
    chart: {
      type: 'bar',
      height: '140px',
      foreColor: '#4B5563',
      fontFamily: 'Inter, sans-serif',
      toolbar: { show: false },
    },
    theme: { monochrome: { enabled: true, color: '#1A56DB' } },
    plotOptions: {
      bar: {
        columnWidth: '25%',
        borderRadius: 3,
        colors: {
          backgroundBarColors: signupsChartColors.backgroundBarColors,
          backgroundBarRadius: 3,
        },
      },
      dataLabels: { hideOverflowingLabels: false },
    },
    xaxis: {
      floating: false,
      labels: { show: false },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    tooltip: {
      shared: true,
      intersect: false,
      style: { fontSize: '14px', fontFamily: 'Inter, sans-serif' },
    },
    states: { hover: { filter: { type: 'darken', value: 0.8 } } },
    fill: { opacity: 1 },
    yaxis: { show: false },
    grid: { show: false },
    dataLabels: { enabled: false },
    legend: { show: false },
  };
};

// Montaje de los charts dependientes del DOM
window.addEventListener('load', function () {
  // Visitors chart
  const visitorsEl = document.getElementById('visitors-chart');
  if (visitorsEl) {
    const chart = new ApexCharts(visitorsEl, getVisitorsChartOptions());
    chart.render();
    document.addEventListener('dark-mode', function () {
      chart.updateOptions(getVisitorsChartOptions());
    });
  }

  // Week signups chart
  const signupsEl = document.getElementById('week-signups-chart');
  if (signupsEl) {
    const chart = new ApexCharts(signupsEl, getSignupsChartOptions());
    chart.render();
    document.addEventListener('dark-mode', function () {
      chart.updateOptions(getSignupsChartOptions());
    });
  }
});