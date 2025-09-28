/**
 * Loading Spinner Component
 * AI 응답 대기 중 표시되는 로딩 인디케이터
 */

'use client';

import { LoadingSpinnerProps } from '../types/api.types';

export default function LoadingSpinner({
  message = "AI가 답변을 생각하고 있어요...",
  size = 'medium'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  const containerClasses = {
    small: 'space-x-2',
    medium: 'space-x-3',
    large: 'space-x-4'
  };

  const textClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  };

  return (
    <div className={`flex items-center justify-center ${containerClasses[size]}`}>
      {/* 회전하는 스피너 */}
      <div
        className={`
          animate-spin rounded-full border-2 border-blue-200 border-t-blue-600
          ${sizeClasses[size]}
        `}
        aria-label="로딩 중"
        role="status"
      />

      {/* 타이핑 애니메이션 */}
      <div className="flex items-center space-x-1">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
        </div>

        {/* 메시지 */}
        {message && (
          <span className={`text-gray-600 font-medium ${textClasses[size]} ml-2`}>
            {message}
          </span>
        )}
      </div>
    </div>
  );
}

// 인라인 로딩 스피너 (작은 버전)
export function InlineSpinner({ className = '' }: { className?: string }) {
  return (
    <div
      className={`
        inline-block w-4 h-4 border-2 border-gray-300 border-t-gray-600
        rounded-full animate-spin ${className}
      `}
      aria-label="로딩 중"
      role="status"
    />
  );
}

// 풀스크린 로딩 오버레이
export function LoadingOverlay({
  message = "페이지를 로드하고 있습니다...",
  isVisible = true
}: {
  message?: string;
  isVisible?: boolean;
}) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 shadow-2xl">
        <LoadingSpinner message={message} size="large" />
      </div>
    </div>
  );
}

// 버튼 내부 로딩 스피너
export function ButtonSpinner() {
  return (
    <div
      className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
      aria-label="로딩 중"
      role="status"
    />
  );
}

// 카드/섹션용 로딩 스켈레톤
export function LoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="flex space-x-4">
        <div className="rounded-full bg-gray-300 h-10 w-10"></div>
        <div className="flex-1 space-y-2 py-1">
          <div className="h-4 bg-gray-300 rounded w-3/4"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-300 rounded"></div>
            <div className="h-4 bg-gray-300 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    </div>
  );
}

// 메시지 로딩용 특수 스피너
export function MessageLoadingSpinner() {
  return (
    <div className="flex items-center space-x-2 p-4 bg-gray-50 rounded-lg border">
      <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
        🤖
      </div>
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
      </div>
      <span className="text-gray-500 text-sm">AI가 답변을 준비하고 있어요</span>
    </div>
  );
}