/**
 * Error Boundary Component
 * React 에러 경계 및 에러 처리 컴포넌트
 */

'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: any) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: any;
}

// React Error Boundary 클래스 컴포넌트
export class TutorErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    this.setState({ error, errorInfo });
    this.props.onError?.(error, errorInfo);

    // 개발 모드에서 콘솔에 에러 로깅
    if (process.env.NODE_ENV === 'development') {
      console.error('TutorErrorBoundary caught an error:', error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorFallback
          error={this.state.error}
          onRetry={this.handleRetry}
          errorInfo={this.state.errorInfo}
        />
      );
    }

    return this.props.children;
  }
}

// 에러 폴백 UI 컴포넌트
interface ErrorFallbackProps {
  error?: Error;
  onRetry?: () => void;
  errorInfo?: any;
}

function ErrorFallback({ error, onRetry, errorInfo }: ErrorFallbackProps) {
  const isDev = process.env.NODE_ENV === 'development';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-4">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
            <span className="text-2xl">😵</span>
          </div>
          <div className="ml-4">
            <h2 className="text-lg font-semibold text-gray-900">
              오류가 발생했습니다
            </h2>
            <p className="text-gray-600 text-sm">
              튜터 시스템에 예상치 못한 문제가 발생했습니다.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
            <p className="text-red-800 text-sm font-medium">
              {error.message || '알 수 없는 오류가 발생했습니다.'}
            </p>
          </div>
        )}

        <div className="flex space-x-3">
          <button
            onClick={onRetry}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            다시 시도
          </button>
          <button
            onClick={() => window.location.reload()}
            className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
          >
            페이지 새로고침
          </button>
        </div>

        {isDev && error && (
          <details className="mt-4">
            <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
              개발자 정보 (개발 모드만 표시)
            </summary>
            <div className="mt-2 p-3 bg-gray-100 rounded text-xs font-mono">
              <div className="mb-2">
                <strong>Error:</strong> {error.toString()}
              </div>
              <div className="mb-2">
                <strong>Stack:</strong>
                <pre className="whitespace-pre-wrap text-xs">
                  {error.stack}
                </pre>
              </div>
              {errorInfo && (
                <div>
                  <strong>Component Stack:</strong>
                  <pre className="whitespace-pre-wrap text-xs">
                    {errorInfo.componentStack}
                  </pre>
                </div>
              )}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}

// API 에러 표시 컴포넌트
interface APIErrorProps {
  error: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  type?: 'inline' | 'banner' | 'modal';
}

export function APIError({
  error,
  onRetry,
  onDismiss,
  type = 'inline'
}: APIErrorProps) {
  const baseClasses = "flex items-center justify-between p-4 border rounded-lg";
  const typeClasses = {
    inline: "bg-red-50 border-red-200",
    banner: "bg-red-600 text-white border-red-600",
    modal: "bg-white border-red-200 shadow-lg"
  };

  return (
    <div className={`${baseClasses} ${typeClasses[type]}`}>
      <div className="flex items-center space-x-3">
        <span className="text-xl">
          {type === 'banner' ? '⚠️' : '❌'}
        </span>
        <div>
          <p className={`font-medium ${
            type === 'banner' ? 'text-white' : 'text-red-800'
          }`}>
            API 오류
          </p>
          <p className={`text-sm ${
            type === 'banner' ? 'text-red-100' : 'text-red-600'
          }`}>
            {error}
          </p>
        </div>
      </div>

      <div className="flex space-x-2">
        {onRetry && (
          <button
            onClick={onRetry}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              type === 'banner'
                ? 'bg-red-500 text-white hover:bg-red-400'
                : 'bg-red-100 text-red-700 hover:bg-red-200'
            }`}
          >
            재시도
          </button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={`px-2 py-1 text-sm rounded transition-colors ${
              type === 'banner'
                ? 'text-white hover:bg-red-500'
                : 'text-red-500 hover:text-red-700'
            }`}
            aria-label="에러 메시지 닫기"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}

// 네트워크 연결 오류 컴포넌트
export function NetworkError({ onRetry }: { onRetry?: () => void }) {
  return (
    <div className="text-center py-8">
      <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-3xl">📡</span>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        연결 문제가 발생했습니다
      </h3>
      <p className="text-gray-600 mb-4">
        서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요.
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          다시 연결 시도
        </button>
      )}
    </div>
  );
}

// 서버 오류 컴포넌트
export function ServerError({ onRetry }: { onRetry?: () => void }) {
  return (
    <div className="text-center py-8">
      <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-3xl">🔧</span>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        서버 오류가 발생했습니다
      </h3>
      <p className="text-gray-600 mb-4">
        일시적인 서버 문제입니다. 잠시 후 다시 시도해주세요.
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          다시 시도
        </button>
      )}
    </div>
  );
}

// 타임아웃 오류 컴포넌트
export function TimeoutError({ onRetry }: { onRetry?: () => void }) {
  return (
    <div className="text-center py-8">
      <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-3xl">⏰</span>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        요청 시간이 초과되었습니다
      </h3>
      <p className="text-gray-600 mb-4">
        AI 처리 시간이 예상보다 길어지고 있습니다. 다시 시도해주세요.
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          다시 시도
        </button>
      )}
    </div>
  );
}