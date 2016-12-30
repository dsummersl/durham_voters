require('./app.css')

const choo = require('choo')
const d3 = require('d3')
const extend = require('xtend')
const html = require('choo/html')
const _ = require('lodash')
const topojson = require('topojson-client')

const app = choo()
app.model({
  state: {
    names: [ '...loading...' ],
    choiceIndex: 0,
    csvData: [ ],
    filteredCsvData: [],
    precincts: null
  },
  effects: {
    loadData: (data, state, send, done) => {
      var loaded = _.after(3, done)

      d3.csv('./president.csv', (d) => {
        return {
          Precinct: d.Precinct,
          County: d.County,
          Choice: d.Choice,
          Total_Votes: +d.Total_Votes
        }
      }, (rows) => {
        send('processElectionData', rows, loaded)
      })
      d3.json("./Precincts.topojson", (error, nc) => {
        if (error) return console.log(error)

        const boundaries = topojson.feature(nc, nc.objects.Precincts)
        send('receiveTopoJson', boundaries, loaded)
      })
    },
    processElectionData: (csv, state, send, done) => {
      const names = _.chain(csv).map('Choice').uniq().value()
      const filtered = _.filter(csv, { 'Choice': names[state.choiceIndex] })
      send('receiveElectionData', {
        names: names,
        csvData: csv,
        filteredCsvData: filtered,
      }, done)
    },
    selectName: (data, state, send, done) => {
      send('receiveChoiceIndex', data, (err, res) => {
        if (err) return console.log(err)
        send('processElectionData', res.csvData, done)
      })
    }
  },
  reducers: {
    receiveElectionData: (data, state) => {
      return extend(state, {
        names: data.names,
        csvData: data.csvData,
        filteredCsvData: data.filteredCsvData
      })
    },
    receiveTopoJson: (data, state) => {
      return extend(state, {
        precincts: data
      })
    },
    receiveChoiceIndex: (data, state) => {
      return extend(state, {
        choiceIndex: +data.choiceIndex
      })
    }
  }
})

const mapElement = (() => {
  const el = document.createElement('div')
  el.classList.add('map')

  let svg = d3.select(el).append("svg")
      .attr("width", '100%')

  let projection = d3.geoAlbers()
      .scale(1)
      .translate([0, 0])
      .rotate([79.6,-34.5,-1])

  let path = d3.geoPath()
      .projection(projection)

  // let onSizeChange = () => {
  //   // TODO not quite working.
  //   const newWidth = el.offsetWidth
  //   d3.select('svg > g').attr('transform', `scale(${ newWidth / width })`)
  //   d3.select('svg').style('height', height * (newWidth / width))
  // }
  //
  // d3.select(window).on('resize', onSizeChange)

  return (state) => {
    if (!state.precincts || state.filteredCsvData.length == 0) {
      return el
    }

    // Compute the bounds of a feature of interest, then derive scale & translate.
    const b = path.bounds(state.precincts)

    // height / width
    const ratio = (b[1][1] - b[0][1]) / (b[1][0] - b[0][0])
    const width = el.offsetWidth
    const height = width * ratio
    d3.select('svg').style('height', height)

    const s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height)
    const t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2]

    projection.scale(s)
        .translate(t)

    const maxValue = _.maxBy(state.csvData, 'Total_Votes').Total_Votes
    const color = d3.scaleLinear()
      .domain([0, maxValue])
      .range(["black", "green"])

    const svgBound = svg.selectAll('path').data(state.precincts.features)

    svgBound.enter()
      .append('path')
        .attr('class', 'county')
        .attr('d', path)
      .merge(svgBound)
        .transition()
        .delay(500)
        .duration(1000)
        .style('fill', (d) => {
          const match = _.filter(state.filteredCsvData, {
            'Precinct': d.properties.PREC_ID,
            'County': d.properties.COUNTY_NAM
          })
          if (match.length === 0) {
            return color(0)
          }
          return color(match[0].Total_Votes)
        })

    return el
  }
})()

const view = (state, prev, send) => {
  return html`
    <div onload=${() => send('loadData')}>
      <div class="container-fluid">
        <nav class="navbar navbar-fixed-top navbar-dark bg-primary">
          <ul class="nav navbar-nav">
            <form class="form-inline float-xs-left">
              <label for="selectData">Data</label>
              <select class="form-control" id="selectData" onchange=${(e) => {
                send('selectName', { choiceIndex: e.target.value })
              }}>
                ${state.names.map((name, index) => html`
                    <option value="${index}" ${index == state.choiceIndex ? 'selected':''}>${name}</option>
                  `)}
              </select>
            </form>
          </ul>
        </nav>
      </div>

      ${mapElement(state)}
    </div>`
}

app.router((route) => [
  route('/', view)
])

const tree = app.start()
document.body.appendChild(tree)
