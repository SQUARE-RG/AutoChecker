#include <string>

class DynamicText {
public:
    explicit DynamicText(const std::string& value);
    DynamicText(const DynamicText& other);
    DynamicText& operator=(const DynamicText& other);
    ~DynamicText();
private:
    std::string* text;
};

DynamicText::DynamicText(const std::string& value) : text(new std::string(value)) {}
DynamicText::DynamicText(const DynamicText& other) : text(new std::string(*other.text)) {}
DynamicText& DynamicText::operator=(const DynamicText& other) {
    if (this != &other) {
        *text = *other.text;
    }
    return *this;
}
DynamicText::~DynamicText() { delete text; }

int main() {
    DynamicText first("alpha");
    DynamicText second(first);
    first = second;
    return 0;
}
