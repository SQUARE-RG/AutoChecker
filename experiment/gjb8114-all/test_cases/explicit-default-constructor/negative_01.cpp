#include <cstdlib>

class Counter { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
public:
    ~Counter() {}
    void Set(int value) { value_ = value; }
    int Get() const { return value_; }
private:
    int value_ = 0;
};

int main() {
    Counter c;
    c.Set(7);
    return c.Get();
}
