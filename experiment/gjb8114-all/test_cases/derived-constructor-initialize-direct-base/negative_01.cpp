#include <iostream>

class Document {
public:
    Document() : docid(0) {}
    explicit Document(int value) : docid(value) {}
    int docid;
};

class Book : public Document {
public:
    int bookid;
    Book() : bookid(1) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
    {}
};

int main() {
    Book mybook;
    std::cout << mybook.bookid << '\n';
    return 0;
}
