template <typename T>
struct Bits {
    T payload;
    signed int flag : 2;
};

int main() {
    Bits<int> b{};
    b.flag = -1;
    return 0;
}
