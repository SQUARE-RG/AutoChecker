class Abstract {
public:
    virtual void run() = 0;
    Abstract& operator=(Abstract const& rhs) noexcept; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-4]
protected:
    int state = 0;
};

Abstract& Abstract::operator=(Abstract const& rhs) noexcept {
    state = rhs.state;
    return *this;
}

class Impl : public Abstract {
public:
    void run() override {}
};

int main() {
    return 0;
}
