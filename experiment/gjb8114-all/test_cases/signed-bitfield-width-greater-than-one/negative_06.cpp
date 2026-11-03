template <typename T>
struct Bits {
    T payload;
    signed int flag : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
};

int main() {
    Bits<int> b{};
    b.flag = -1;
    return 0;
}
