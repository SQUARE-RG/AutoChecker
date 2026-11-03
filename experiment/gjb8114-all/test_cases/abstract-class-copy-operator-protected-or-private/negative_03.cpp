#include <cstdint>

class AbstractWidget {
public:
    virtual ~AbstractWidget() = default;
    virtual int size() const = 0;

    AbstractWidget& operator=(AbstractWidget const& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-4]
        value_ = rhs.value_;
        return *this;
    }

private:
    int value_ = 0;
};

class WidgetImpl final : public AbstractWidget {
public:
    int size() const override { return 1; }
};

int main() {
    WidgetImpl widget;
    return widget.size();
}
