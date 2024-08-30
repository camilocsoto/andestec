import ApexCharts from 'apexcharts';
// extract the data from the array
const dataContainer = document.getElementById('data-container-charts');
let chartsData = JSON.parse(dataContainer.getAttribute('data-charts'));
//main chart
let hoursData = chartsData.hour;
let capacitiesData = chartsData.capacitiy;
let outputData = chartsData.output;
// second chart
let temperature = chartsData.temp;

const getMainChartOptions = () => {
	let mainChartColors = {}

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
		}
	}

	return {
		chart: {
			height: 420,
			type: 'area',
			fontFamily: 'Inter, sans-serif',
			foreColor: mainChartColors.labelColor,
			toolbar: {
				show: false
			}
		},
		fill: {
			type: 'gradient',
			gradient: {
				enabled: true,
				opacityFrom: mainChartColors.opacityFrom,
				opacityTo: mainChartColors.opacityTo
			}
		},
		dataLabels: {
			enabled: false
		},
		tooltip: {
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif',
			},
		},
		grid: {
			show: true,
			borderColor: mainChartColors.borderColor,
			strokeDashArray: 1,
			padding: {
				left: 35,
				bottom: 15
			}
		},
		series: [
			{
				name: 'current % of gas (%)',
				data: capacitiesData,
				color: '#1A56DB'
			},
			{
				name: 'current % output force of gas',
				data: outputData,
				color: '#FDBA8C'
			}
		],
		markers: {
			size: 5,
			strokeColors: '#ffffff',
			hover: {
				size: undefined,
				sizeOffset: 3
			}
		},
		xaxis: {
			categories: hoursData,
			labels: {
				style: {
					colors: [mainChartColors.labelColor],
					fontSize: '14px',
					fontWeight: 500,
				},
			},
			axisBorder: {
				color: mainChartColors.borderColor,
			},
			axisTicks: {
				color: mainChartColors.borderColor,
			},
			crosshairs: {
				show: true,
				position: 'back',
				stroke: {
					color: mainChartColors.borderColor,
					width: 1,
					dashArray: 10,
				},
			},
		},
		yaxis: {
			labels: {
				style: {
					colors: [mainChartColors.labelColor],
					fontSize: '14px',
					fontWeight: 500,
				},
				formatter: function (value) {
					return  value + '%';
				}
			},
		tickAmount: 10, // Asegura que haya 10 intervalos
		min: 0,
		max: 100,
		forceNiceScale: true, // Asegura que los valores sean agradables visualmente
		},
		legend: {
			fontSize: '14px',
			fontWeight: 500,
			fontFamily: 'Inter, sans-serif',
			labels: {
				colors: [mainChartColors.labelColor]
			},
			itemMargin: {
				horizontal: 10
			}
		},
		responsive: [
			{
				breakpoint: 1024,
				options: {
					xaxis: {
						labels: {
							show: false
						}
					}
				}
			}
		]
	};
}
if (document.getElementById('main-chart')) {
	const chart = new ApexCharts(document.getElementById('main-chart'), getMainChartOptions());
	chart.render();

	// init again when toggling dark mode
	document.addEventListener('dark-mode', function () {
		chart.updateOptions(getMainChartOptions());
	});
}
//  current capacity chart 🔥
if (document.getElementById('new-products-chart')) {
	// data for this chart
	let capacity_serie = hoursData.map((time, index) => {
		return {x: time, y: capacitiesData[index]};
	});
	const options = {
		colors: ['#1A56DB', '#FDBA8C'],
		series: [
			{
				name: '% of gas',
				color: '#1A56DB',
				data: capacity_serie
			}
		],
		chart: {
			type: 'bar',
			height: '140px',
			fontFamily: 'Inter, sans-serif',
			foreColor: '#4B5563',
			toolbar: {
				show: false
			}
		},
		plotOptions: {
			bar: {
				columnWidth: '90%',
				borderRadius: 3
			}
		},
		tooltip: {
			shared : false,
			intersect: false,
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			},
		},
		states: {
			hover: {
				filter: {
					type: 'darken',
					value: 1
				}
			}
		},
		stroke: {
			show: true,
			width: 5,
			colors: ['transparent']
		},
		grid: {
			show: false
		},
		dataLabels: {
			enabled: false
		},
		legend: {
			show: false
		},
		xaxis: {
			floating: false,
			labels: {
				show: false
			},
			axisBorder: {
				show: false
			},
			axisTicks: {
				show: false
			},
		},
		yaxis: {
			labels: false
		},
		fill: {
			opacity: 1
		}
	};

	const chart = new ApexCharts(document.getElementById('new-products-chart'), options);
	chart.render();
}

// current output of gas 🔥
const getVisitorsChartOptions = () => {
	let visitorsChartColors = {}

	if (document.documentElement.classList.contains('dark')) {
		visitorsChartColors = {
			fillGradientShade: 'dark',
			fillGradientShadeIntensity: 0.45,
		};
	} else {
		visitorsChartColors = {
			fillGradientShade: 'light',
			fillGradientShadeIntensity: 1,
		}
	}

	return {
		series: [{
			name: 'Pressure',
			data: outputData
		}],
		labels: hoursData,
		chart: {
			type: 'area',
			height: '305px',
			fontFamily: 'Inter, sans-serif',
			sparkline: {
				enabled: true
			},
			toolbar: {
				show: false
			}
		},
		fill: {
			type: 'gradient',
			gradient: {
				shade: visitorsChartColors.fillGradientShade,
				shadeIntensity: visitorsChartColors.fillGradientShadeIntensity
			},
		},
		plotOptions: {
			area: {
				fillTo: 'end'
			}
		},
		theme: {
			monochrome: {
				enabled: true,
				color: '#1A56DB',
			}
		},
		tooltip: {
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			},
		},
	}
}

const getSignupsChartOptions = () => {
	let signupsChartColors = {}

	if (document.documentElement.classList.contains('dark')) {
		signupsChartColors = {
			backgroundBarColors: ['#374151', '#374151', '#374151', '#374151', '#374151', '#374151', '#374151']
		};
	} else {
		signupsChartColors = {
			backgroundBarColors: ['#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB']
		};
	}

	return {
		series: [{
			name: 'output of gas',
			data: outputData
		}],
		labels: hoursData,
		chart: {
			type: 'bar',
			height: '140px',
			foreColor: '#4B5563',
			fontFamily: 'Inter, sans-serif',
			toolbar: {
				show: false
			}
		},
		theme: {
			monochrome: {
				enabled: true,
				color: '#1A56DB'
			}
		},
		plotOptions: {
			bar: {
				columnWidth: '25%',
				borderRadius: 3,
				colors: {
					backgroundBarColors: signupsChartColors.backgroundBarColors,
					backgroundBarRadius: 3
				},
			},
			dataLabels: {
				hideOverflowingLabels: false
			}
		},
		xaxis: {
			floating: false,
			labels: {
				show: false
			},
			axisBorder: {
				show: false
			},
			axisTicks: {
				show: false
			},
		},
		tooltip: {
			shared: true,
			intersect: false,
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			}
		},
		states: {
			hover: {
				filter: {
					type: 'darken',
					value: 0.8
				}
			}
		},
		fill: {
			opacity: 1
		},
		yaxis: {
			show: false
		},
		grid: {
			show: false
		},
		dataLabels: {
			enabled: false
		},
		legend: {
			show: false
		},
	};
}

if (document.getElementById('week-signups-chart')) {
	const chart = new ApexCharts(document.getElementById('week-signups-chart'), getSignupsChartOptions());
	chart.render();

	// init again when toggling dark mode
	document.addEventListener('dark-mode', function () {
		chart.updateOptions(getSignupsChartOptions());
	});
}

/* hasta aquí

const pieChartOptions = (data) => {

	let trafficChannelsChartColors = {}

	if (document.documentElement.classList.contains('dark')) {
		trafficChannelsChartColors = {
			strokeColor: '#1f2937'
		};
	} else {
		trafficChannelsChartColors = {
			strokeColor: '#ffffff'
		}
	}

	return {
		series: data.map(dt => dt.price),
		labels: data.map(dt => dt.name),
		colors: ['#16BDCA', '#FDBA8C', '#1A56DB'],
		chart: {
			type: 'donut',
			height: 400,
			fontFamily: 'Inter, sans-serif',
			toolbar: {
				show: false
			},
		},
		responsive: [{
			breakpoint: 430,
			options: {
			  chart: {
				height: 300
			  }
			}
		}],
		stroke: {
			colors: [trafficChannelsChartColors.strokeColor]
		},
		states: {
			hover: {
				filter: {
					type: 'darken',
					value: 0.9
				}
			}
		},
		tooltip: {
			shared: true,
			followCursor: false,
			fillSeriesColor: false,
			inverseOrder: true,
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			},
			x: {
				show: true,
				formatter: function (_, { seriesIndex, w }) {
					const label = w.config.labels[seriesIndex];
					return label
				}
			},
			y: {
				formatter: function (value) {
					return value;
				}
			}
		},
		grid: {
			show: false
		},
		dataLabels: {
			enabled: false
		},
		legend: {
			show: false
		},
	};
}

if (document.getElementById('products-bar-chart-api')) {
    const apiUrl = '/api/product/';
	let dt = []

	const fetchData = async () => {
		try {
			const response = await fetch(apiUrl);
			const data = await response.json();
			dt = data
		} catch (error) {
			console.error('Error fetching data:', error);
		}
	};
	await fetchData();
	
	const options = {
		colors: ['#1A56DB', '#FDBA8C'],
		series: [
			{
				name: 'Product',
				color: '#1A56DB',
				data: dt.map(product => ({ x: product.name, y: product.price }))
			},
		],
		chart: {
			type: 'bar',
			height: '420px',
			fontFamily: 'Inter, sans-serif',
			foreColor: '#4B5563',
			toolbar: {
				show: false
			}
		},
		plotOptions: {
			bar: {
				columnWidth: '90%',
				borderRadius: 3
			}
		},
		tooltip: {
			shared : true,
			intersect: false,
			style: {
				fontSize: '14px',
				fontFamily: 'Inter, sans-serif'
			},
		},
		states: {
			hover: {
				filter: {
					type: 'darken',
					value: 1
				}
			}
		},
		stroke: {
			show: true,
			width: 5,
			colors: ['transparent']
		},
		grid: {
			show: false
		},
		dataLabels: {
			enabled: false
		},
		legend: {
			show: false
		},
		xaxis: {
			floating: false,
			labels: {
				show: false
			},
			axisBorder: {
				show: false
			},
			axisTicks: {
				show: false
			},
		},
		yaxis: {
			show: false
		},
		fill: {
			opacity: 1
		}
	};

	const chart = new ApexCharts(document.getElementById('products-bar-chart-api'), options); 
	chart.render();
}

if (document.getElementById('products-pie-chart-api')) {
	const apiUrl = '/api/product/';
	let dt = []

	const fetchData = async () => {
		try {
			const response = await fetch(apiUrl);
			const data = await response.json();
			dt = data
		} catch (error) {
			console.error('Error fetching data:', error);
		}
	};
	await fetchData();


	const chart = new ApexCharts(document.getElementById('products-pie-chart-api'), pieChartOptions(dt));
	chart.render();

	// init again when toggling dark mode
	document.addEventListener('dark-mode', function () {
		chart.updateOptions(pieChartOptions(dt));
	});
}
*/