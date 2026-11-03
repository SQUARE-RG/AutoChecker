class IntHolder {
public:
    explicit IntHolder(int* ptr) : ptr_(ptr) {}

    int* get() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]
        return ptr_;
    }

private:
    int* ptr_;
};

int main() {
    int values[2] = {1, 2};
    IntHolder holder(values);
    int* exposed = holder.get();
    exposed[0] = 9;
    return values[0] == 9 ? 0 : 1;
}
