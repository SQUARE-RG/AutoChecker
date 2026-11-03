template <class T, int N> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]
struct FixedArray {
    T data[N];
};

int main() {
    FixedArray<int, 3> arr{};
    arr.data[0] = 1;
    return arr.data[0];
}
