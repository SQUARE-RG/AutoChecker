class Abstract {
public:
    virtual void run() = 0;
private:
    Abstract& operator=(Abstract const& rhs) {
        state = rhs.state;
        return *this;
    }
    int state = 0;
};

class Impl : public Abstract {
public:
    void run() override {}
};

int main() {
    return 0;
}
