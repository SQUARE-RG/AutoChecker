#include <exception>

class CleanupError : public std::exception {
public:
    const char* what() const noexcept override { return "cleanup failure"; }
};

class Widget {
public:
    Widget() = default;
    ~Widget() noexcept(false);
};

Widget::~Widget() noexcept(false) {
    throw CleanupError{}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-2]
}

int main() {
    try {
        Widget w;
    } catch (const CleanupError&) {
    }
    return 0;
}
