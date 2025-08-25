'use client'

import { useState } from 'react'
import { Link } from 'react-router-dom'


export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="bg-white font-sans overflow-x-hidden">
      <header className="absolute inset-x-0 top-0 z-50">
        <nav className="flex items-center justify-between p-6 lg:px-8">
          <div className="flex lg:flex-1">
            <a href="#" className="-m-1.5 p-1.5">
              <span className="sr-only">HireSense</span>
              <img
                alt=""
                src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=600"
                className="h-8 w-auto"
              />
            </a>
          </div>
        </nav>
      </header>

      <main className="relative isolate overflow-hidden px-6 pt-32 lg:px-8">
        {/* Top blurred background */}
        <div
          aria-hidden="true"
          className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
        >
          <div
            className="relative left-1/2 -translate-x-1/2 w-[72rem] aspect-[1155/678] rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30"
            style={{
              clipPath:
                'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
            }}
          />
        </div>

        {/* Hero content */}
        <div className="mx-auto max-w-2xl text-center py-20 sm:py-28 lg:py-32">
          <h1 className="font-[Montserrat] text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-gray-900 leading-tight">
            HireSense Resume Shortlister
          </h1>
          <p className=" font-[Montserrat] mt-6 text-xl sm:text-2xl text-gray-600 font-medium">
            Empower your hiring process with AI-driven resume matching. Smart. Fast. Reliable.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link
              to="/shortlister"
              className="font-[Montserrat] rounded-md bg-indigo-600 px-6 py-3 text-base font-semibold text-white shadow-md hover:bg-indigo-500 transition duration-300"
            >
              Get Started
            </Link>
          </div>
        </div>

        {/* Bottom blurred background */}
        <div
          aria-hidden="true"
          className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]"
        >
          <div
            className="relative left-1/2 -translate-x-1/2 w-[72rem] aspect-[1155/678] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30"
            style={{
              clipPath:
                'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
            }}
          />
        </div>
      </main>
    </div>
  )
}
