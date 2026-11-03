struct PureBase {
    virtual void execute() = 0;
    virtual ~PureBase() = default;
};

struct PureDerived : PureBase {
    virtual void execute() = 0;
};

int main() {
    return 0;
}
