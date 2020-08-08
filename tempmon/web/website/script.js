var myChart

async function getTemps(year, month, day) {
  raw = await fetch("/", {
    method: "POST",
    headers: {"Content-Type": "application/json; charset=UTF-8"},
    body: JSON.stringify({year, month, day})
  })
  resp = await raw.json()
  return resp
}


function addChart() {
  var ctx = document.getElementById('myChart').getContext('2d');
  myChart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [{
        label: 'Temperature',
        data: [],
        backgroundColor: "rgba(0, 0, 255, 0.7)",
        borderColor: "rgba(0, 0, 255, 0.3)",
        fill: false,
      }]
    },
    options: {
      elements: {
        line: {
          tension: 0
        }
      },
      animation: {
        duration: 0
      },
      responsiveAnimationDuration: 0,
      maintainAspectRatio: false,
      scales: {
        xAxes: [{
          type: "time",
          time: {
            unit: "hour",
            displayFormats: {
              hour: "H"
            },
            tooltipFormat: "HH:mm:ss",
          }
        }]
      }
    }
  })
}

function cleanup(data) {
  if (data.length <= 2) {
    return data
  }

  let anchor = 0
  let newData = []
  newData.push(data[0])
  for (let i = 2; i < data.length; i++) {
    if (data[anchor][1] === data[i][1] && data[anchor][1] === data[i-1][1]) {
    } else {
      newData.push(data[i-1])
      anchor = i - 1
    }

  }
  newData.push(data[data.length - 1])

  return newData
}

function lowPass(data) {
  if (data.length <= 2) {
    return data
  }

  let newData = []
  newData.push(data[0])
  for (let i = 2; i < data.length; i++) {
    if (data[i-2][1] === data[i][1] && data[i-2][1] !== data[i-1][1]) {
      newData.push(data[i])
      i += 1
    } else {
      newData.push(data[i-1])
    }

  }
  newData.push(data[data.length - 1])

  return newData
}

function beautify(data) {
  if (data.length <= 1) {
    return data
  }

  let newData = []
  let i
  for (i = 1; i < data.length; i++) {
    if (data[i-1][1] === data[i][1]) {
      let middle = Math.floor((data[i][0] + data[i-1][0]) / 2)
      let temp = data[i][1]
      newData.push([middle, temp])
      i += 1
    } else {
      newData.push(data[i-1])
    }
  }

  // i === data.length + 1 if the two last points got merged
  if (i === data.length) {
    newData.push(data[i - 1])
  }

  return newData
}

async function updateChart(year, month, day, lp=false, be=false) {
  data = await getTemps(year, month, day)

  if (lp) {
    data = cleanup(lowPass(data))
  }

  if (be) {
    data = beautify(data)
    myChart.options.elements.line.tension = 0.4
  } else {
    myChart.options.elements.line.tension = 0
  }

  myChart.data.datasets[0].data = data.map(e => {
    return {
      y: e[1] / 1000,
      x: new Date(
        year,
        month - 1,
        day,
        Math.floor(e[0] / 3600),
        Math.floor((e[0] % 3600) / 60),
        e[0] % 60
      )
    }
  })
  myChart.update()
}

function updateClick() {
  let dp = document.getElementById("datePicker")
  let lp = document.getElementById("lowPassBox")
  let be = document.getElementById("beautifyBox")

  dp.disabled = true
  lp.disabled = true
  be.disabled = true
  let date = new Date(document.getElementById("datePicker").value)
  if (date !== "") {
    updateChart(date.getFullYear(), date.getMonth() + 1, date.getDate(), lp.checked, be.checked)
      .then(() => {
        dp.disabled = false
        lp.disabled = false
        be.disabled = false
      })
      .catch(e => console.error(e))
  }
}

window.addEventListener("DOMContentLoaded", () => {
  addChart()
  let now = new Date()
  let y = now.getFullYear()
  let m = (now.getMonth()+1).toString().padStart(2, "0")
  let d = now.getDate().toString().padStart(2, "0")
  let dp = document.getElementById("datePicker")
  dp.value = `${y}-${m}-${d}`
  dp.onchange()
})
