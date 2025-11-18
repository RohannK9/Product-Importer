import type { PropsWithChildren } from "react";
import { Link, NavLink } from "react-router-dom";
import "./Layout.css";

const navItems = [
  { to: "/upload", label: "CSV Upload" },
  { to: "/products", label: "Products" },
  { to: "/webhooks", label: "Webhooks" },
];

export function Layout({ children }: PropsWithChildren) {
  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <Link to="/" className="app-logo">
          Product Importer
        </Link>
        <nav className="app-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? "app-nav__link app-nav__link--active" : "app-nav__link"
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="app-content">{children}</main>
    </div>
  );
}
