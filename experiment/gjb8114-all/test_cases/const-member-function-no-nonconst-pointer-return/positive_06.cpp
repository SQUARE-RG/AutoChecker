class MutableScalar {
public:
    MutableScalar() : value(0) {}

    // 遵循：const 成员函数返回 mutable 标量成员的 const 引用
    const int& get() const {
        return value;
    }

private:
    mutable int value;
};

int main() {
    const MutableScalar obj;
    int value = obj.get();
    (void)value;
    return 0;
}
