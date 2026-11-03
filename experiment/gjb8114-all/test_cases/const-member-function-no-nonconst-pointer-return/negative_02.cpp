class IntHolder {
public:
    explicit IntHolder(int* ptr) : ptr_(ptr) {}

    int& get() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]
        return *ptr_;
    }

private:
    int* ptr_;
};

int main() {
    int value = 3;
    IntHolder holder(&value);
    int& exposed = holder.get();
    exposed = 7;
    return value == 7 ? 0 : 1;
}
