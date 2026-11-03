#include <cstdio>
#include <cstring>

int main() {
    char buf[16];
    std::memset(buf, 'x', sizeof buf);
    std::memcpy(buf, "hello", 6);
    std::puts(buf);
    return 0;
}
