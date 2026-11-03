#include <cstddef>

class AutoPointerHolder {
public:
    explicit AutoPointerHolder(int* ptr) : data(ptr) {}

    // 违反：const 成员函数使用 auto 推导返回非 const 指针
    auto get() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]
        return data;
    }

private:
    int* data;
};

int main() {
    int value = 1;
    const AutoPointerHolder holder(&value);
    *holder.get() = 2;
    return 0;
}
