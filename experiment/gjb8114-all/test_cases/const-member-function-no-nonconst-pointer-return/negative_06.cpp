class MutableScalar {
public:
    MutableScalar() : value(0) {}

    // 违反：const 成员函数返回 mutable 标量成员的非 const 引用
    int& get() const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]
        return value;
    }

private:
    mutable int value;
};

int main() {
    const MutableScalar obj;
    obj.get() = 42;
    return 0;
}
