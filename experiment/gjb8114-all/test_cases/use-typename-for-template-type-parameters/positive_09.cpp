template <typename T, int N>
struct FixedArray {
    T data[N];
};

int main() {
    FixedArray<int, 3> arr{};
    arr.data[0] = 1;
    return arr.data[0];
}
