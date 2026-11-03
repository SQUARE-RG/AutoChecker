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
    try {
        throw CleanupError{};
    } catch (const CleanupError&) {
    }
}

int main() {
    Widget w;
    return 0;
}
