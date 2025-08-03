import '@testing-library/jest-dom';

declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R;
      toHaveValue(value: string | number | string[]): R;
      toHaveBeenCalledTimes(expected: number): R;
      toHaveBeenCalledWith(...args: any[]): R;
      toHaveBeenCalled(): R;
    }
  }
}

// Extend Jest mock functions
declare module 'jest' {
  interface MockedFunction<T extends (...args: any[]) => any> {
    mockResolvedValue(value: Awaited<ReturnType<T>>): this;
    mockRejectedValue(value: any): this;
    mockReturnValue(value: ReturnType<T>): this;
    mockImplementation(fn?: T): this;
    mockImplementationOnce(fn: T): this;
    mockReset(): this;
    mockClear(): this;
    mockRestore(): void;
    mock: {
      calls: Parameters<T>[];
      results: Array<{
        type: 'return' | 'throw' | 'incomplete';
        value: ReturnType<T> | any;
      }>;
      instances: any[];
    };
  }
}