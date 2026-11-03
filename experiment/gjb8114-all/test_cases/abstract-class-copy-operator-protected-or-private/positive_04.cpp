#include <cstdint>

class AbstractToken {
public:
    virtual ~AbstractToken() = default;
    virtual const char* name() const = 0;

private:
    AbstractToken& operator=(AbstractToken const& rhs);
    int value_ = 0;
};

AbstractToken& AbstractToken::operator=(AbstractToken const& rhs) {
    value_ = rhs.value_;
    return *this;
}

class TokenImpl final : public AbstractToken {
public:
    const char* name() const override { return "token"; }
};

int main() {
    TokenImpl token;
    return token.name()[0];
}
