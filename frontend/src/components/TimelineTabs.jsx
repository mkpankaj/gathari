const TIMELINES = ['1M', '3M', '6M', '9M', '1Y', '1.5Y', '2Y']

export default function TimelineTabs({ value, onChange }) {
  return (
    <div className="timeline-tabs">
      {TIMELINES.map(t => (
        <button
          key={t}
          className={`timeline-tab${value === t ? ' active' : ''}`}
          onClick={() => onChange(t)}
        >
          {t}
        </button>
      ))}
    </div>
  )
}
