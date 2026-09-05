import type { Resource, ResourceType } from '../api/resources'

// Short, scannable label per type — the badge is meant to help a learner
// triage at a glance ("do I need the official docs, or is a blog post
// enough right now"), not to be a taxonomy.
const TYPE_LABELS: Record<ResourceType, string> = {
  official_docs: 'Docs',
  article: 'Article',
  video: 'Video',
  paper: 'Paper',
  repo: 'Repo',
  interactive: 'Interactive',
}

interface LessonResourcesProps {
  resources: Resource[]
}

export function LessonResources({ resources }: LessonResourcesProps) {
  // Nothing curated for this lesson yet — render nothing rather than an
  // empty "Further Reading" heading with no content under it.
  if (resources.length === 0) return null

  return (
    <section className="lesson-resources" aria-label="Further reading">
      <h2 className="lesson-resources__heading">Further Reading</h2>
      <ul className="lesson-resources__list">
        {resources.map((resource) => (
          <li key={resource.id} className="lesson-resources__item">
            <a
              href={resource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="lesson-resources__link"
            >
              <span className="lesson-resources__badge">
                {TYPE_LABELS[resource.resource_type]}
              </span>
              <span className="lesson-resources__title">{resource.title}</span>
            </a>
            <p className="lesson-resources__description">
              {resource.description}
            </p>
          </li>
        ))}
      </ul>
    </section>
  )
}
