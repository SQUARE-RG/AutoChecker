class Abstract {
public:
    virtual void run() = 0;
protected:
    Abstract& operator=(Abstract const&) = default;
private:
    int state = 0;
};

class Impl : public Abstract {
public:
    void run() override {}
};

int main() {
    return 0;
}
