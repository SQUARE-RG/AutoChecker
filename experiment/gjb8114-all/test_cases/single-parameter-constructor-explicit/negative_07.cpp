#include <iostream>
#include <string>

class Label {
public:
    Label(const std::string& text); // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-2-2-3]
    const std::string& get() const;
private:
    std::string text_;
};

Label::Label(const std::string& text) : text_(text) {}
const std::string& Label::get() const { return text_; }

Label make_label() {
    std::string value("hello");
    return value;
}

int main() {
    Label label = make_label();
    std::cout << label.get();
    return 0;
}
