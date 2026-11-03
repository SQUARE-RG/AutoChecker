template <typename T> class Box { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
public:
    T get() const { return value; }
    void set(T v) { value = v; }
private:
    T value;
};

int main() {
    Box<int> b;
    b.set(7);
    return b.get();
}
