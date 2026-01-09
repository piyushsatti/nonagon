import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-[color:var(--note-bg)]/85 border-t border-[color:var(--note-border)] mt-auto backdrop-blur-sm transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 py-8 text-[color:var(--board-ink)]">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-9 h-9 bg-gradient-to-br from-[color:var(--accent)] to-[color:var(--accent-2)] rounded-lg flex items-center justify-center shadow-pin text-[color:var(--note-bg)]">
                <span className="font-display font-bold text-sm">N</span>
              </div>
              <span className="font-display font-semibold tracking-wide">
                Nonagon
              </span>
            </div>
            <p className="text-sm text-[color:var(--board-ink)]/80 max-w-md">
              A comprehensive quest management and adventure tracking system for
              Discord-based tabletop RPG communities.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="font-semibold text-[color:var(--board-ink)] mb-3 text-sm uppercase tracking-wide">
              Resources
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/nonagon-project/nonagon"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[color:var(--board-ink)]/80 hover:text-[color:var(--accent)] transition"
                >
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="/docs"
                  className="text-sm text-[color:var(--board-ink)]/80 hover:text-[color:var(--accent)] transition"
                >
                  Documentation
                </a>
              </li>
              <li>
                <Link
                  to="/guild/demo"
                  className="text-sm text-[color:var(--board-ink)]/80 hover:text-[color:var(--accent)] transition"
                >
                  Demo
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="font-semibold text-[color:var(--board-ink)] mb-3 text-sm uppercase tracking-wide">
              Community
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://discord.gg/nonagon"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[color:var(--board-ink)]/80 hover:text-[color:var(--accent)] transition"
                >
                  Discord Server
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/nonagon-project/nonagon/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[color:var(--board-ink)]/80 hover:text-[color:var(--accent)] transition"
                >
                  Report an Issue
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/nonagon-project/nonagon/blob/main/CONTRIBUTING.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[color:var(--board-ink)]/80 hover:text-[color:var(--accent)] transition"
                >
                  Contributing
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 pt-6 border-t border-[color:var(--note-border)] flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-[color:var(--board-ink)]/70">
            © {currentYear} Nonagon Project. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <a
              href="/privacy"
              className="text-sm text-[color:var(--board-ink)]/70 hover:text-[color:var(--board-ink)] transition"
            >
              Privacy
            </a>
            <a
              href="/terms"
              className="text-sm text-[color:var(--board-ink)]/70 hover:text-[color:var(--board-ink)] transition"
            >
              Terms
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
