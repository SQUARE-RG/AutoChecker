class Abstract {
public:
    virtual void run() = 0;
    Abstract& operator=(Abstract& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-4]
        state = rhs.state;
        return *this;
    }
protected:
    int state = 0;
};

class Impl : public Abstract {
public:
    void run() override {}
};

int main() {
    return 0;
}
