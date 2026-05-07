const CLASS_MAP = {
  'Strong Upward':   'badge-strong-up',
  'Weak Upward':     'badge-weak-up',
  'Neutral':         'badge-neutral',
  'Weak Downward':   'badge-weak-down',
  'Strong Downward': 'badge-strong-down',
}

export default function TrendBadge({ trend }) {
  return <span className={`badge ${CLASS_MAP[trend] ?? 'badge-neutral'}`}>{trend}</span>
}
