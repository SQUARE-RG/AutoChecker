#include <cstddef>

class AutoConstPointerHolder {
public:
    explicit AutoConstPointerHolder(const int* ptr) : data(ptr) {}

    // 遵循：const 成员函数使用 auto 推导返回 const 指针
    auto get() const {
        return data;
    }

private:
    const int* data;
};

int main() {
    int value = 1;
    const AutoConstPointerHolder holder(&value);
    int read = *holder.get();
    (void)read;
    return 0;
}
