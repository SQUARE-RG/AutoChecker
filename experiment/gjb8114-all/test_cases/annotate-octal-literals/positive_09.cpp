#include <iostream>

template<int N>
struct Buffer {
    int data[N];
};

int main()
{
    Buffer<016 /* octal */> buf;
    buf.data[0] = 7;
    std::cout << buf.data[0] << '\n';
    return 0;
}
