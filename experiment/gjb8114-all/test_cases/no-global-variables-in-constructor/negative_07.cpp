#include <iostream>

int gBudget = 42;

class BudgetView {
public:
    BudgetView();
    int read() const;
private:
    const int* source;
};

BudgetView::BudgetView() {
    source = &gBudget; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
}

int BudgetView::read() const {
    return *source;
}

int main() {
    BudgetView view;
    std::cout << view.read() << '\n';
    return 0;
}
