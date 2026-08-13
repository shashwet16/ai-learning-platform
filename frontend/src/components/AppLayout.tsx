import { Outlet } from 'react-router-dom'
import { SiteHeader } from './SiteHeader'

export function AppLayout() {
  return (
    <>
      <SiteHeader />
      <main>
        <Outlet />
      </main>
    </>
  )
}
