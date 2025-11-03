'use client'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  itemsPerPage: number
  totalItems: number
}

export default function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  itemsPerPage,
  totalItems,
}: PaginationProps) {
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  const getPageNumbers = () => {
    const pages: (number | string)[] = []

    if (totalPages <= 5) {
      // Show all pages if total is 5 or less
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
      return pages
    }

    // Always show first page
    pages.push(1)

    if (currentPage <= 3) {
      // Near beginning: show 1 2 3 4 ... last
      for (let i = 2; i <= 4; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(totalPages)
    } else if (currentPage >= totalPages - 2) {
      // Near end: show 1 ... last-3 last-2 last-1 last
      pages.push('...')
      for (let i = totalPages - 3; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Middle: show 1 ... current-1 current current+1 ... last
      pages.push('...')
      pages.push(currentPage - 1)
      pages.push(currentPage)
      pages.push(currentPage + 1)
      pages.push('...')
      pages.push(totalPages)
    }

    return pages
  }

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-6 mt-8 pt-6 border-t border-neutral-800">
      {/* Items info */}
      <div className="text-sm text-neutral-400 flex items-center gap-2">
        <span className="text-neutral-500">Showing</span>
        <span className="text-white font-semibold px-2 py-1 rounded-md bg-neutral-800 border border-neutral-700">
          {startItem}
        </span>
        <span className="text-neutral-500">to</span>
        <span className="text-white font-semibold px-2 py-1 rounded-md bg-neutral-800 border border-neutral-700">
          {endItem}
        </span>
        <span className="text-neutral-500">of</span>
        <span className="text-white font-semibold px-2 py-1 rounded-md bg-neutral-800 border border-neutral-700">
          {totalItems}
        </span>
        <span className="text-neutral-500">items</span>
      </div>

      {/* Pagination controls */}
      <div className="flex items-center gap-2">
        {/* Previous button */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-br from-neutral-800 to-neutral-900 border border-neutral-700 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:from-neutral-700 hover:to-neutral-800 hover:border-neutral-600 active:scale-95 transition-all duration-200 shadow-lg shadow-black/20"
          title="Previous page"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          <span className="hidden sm:inline">Previous</span>
        </button>

        {/* Page numbers */}
        <div className="flex items-center gap-1.5 bg-neutral-900/50 p-1.5 rounded-xl border border-neutral-800">
          {getPageNumbers().map((page, index) => {
            if (page === '...') {
              return (
                <span
                  key={`ellipsis-${index}`}
                  className="px-3 py-2 text-neutral-500 font-medium"
                >
                  ...
                </span>
              )
            }

            const isActive = currentPage === page

            return (
              <button
                key={page}
                onClick={() => onPageChange(page as number)}
                className={`relative px-4 py-2 rounded-lg min-w-[44px] font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30 border border-blue-400 scale-105'
                    : 'bg-neutral-800/50 text-neutral-300 hover:bg-neutral-700 hover:text-white border border-transparent hover:border-neutral-600'
                }`}
              >
                {page}
                {isActive && (
                  <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-blue-400/20 to-transparent pointer-events-none" />
                )}
              </button>
            )
          })}
        </div>

        {/* Next button */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-br from-neutral-800 to-neutral-900 border border-neutral-700 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:from-neutral-700 hover:to-neutral-800 hover:border-neutral-600 active:scale-95 transition-all duration-200 shadow-lg shadow-black/20"
          title="Next page"
        >
          <span className="hidden sm:inline">Next</span>
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>
    </div>
  )
}

