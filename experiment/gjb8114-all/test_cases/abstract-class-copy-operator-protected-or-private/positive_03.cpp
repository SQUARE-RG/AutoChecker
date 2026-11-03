#include <cstdint>

class AbstractNode {
public:
    virtual ~AbstractNode() = default;
    virtual int weight() const = 0;

protected:
    AbstractNode& operator=(AbstractNode const& rhs) {
        value_ = rhs.value_;
        return *this;
    }

private:
    int value_ = 0;
};

class NodeImpl final : public AbstractNode {
public:
    int weight() const override { return 1; }
};

int main() {
    NodeImpl node;
    return node.weight();
}
