import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix stats grid
content = content.replace('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-16 px-2', 'grid grid-cols-2 md:grid-cols-3 gap-6 mb-16 px-2')

# Fix stats padding and radius
content = content.replace('p-8 rounded-[16px]', 'p-4 rounded-xl')
content = content.replace('text-4xl', 'text-2xl')
content = content.replace('text-3xl', 'text-xl')

# Fix loans grid container
content = content.replace('id="loan-container" class="space-y-8"', 'id="loan-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"')

# Replace the Loan Card entirely with a compact one
loan_card_regex = re.compile(r'<div class="bg-surface-container-lowest border border-\[#e8dfa0\] rounded-\[16px\] p-8 flex flex-col md:flex-row items-center md:items-stretch gap-10 transition-colors hover:bg-surface-container group">.*?</form>\s*<button.*?>Renew Info</button>\s*</div>\s*</div>\s*</div>', re.DOTALL)

compact_loan_card = """<div class="bg-surface-container-lowest border border-[#e8dfa0] rounded-xl p-4 flex gap-4 transition-colors hover:bg-surface-container group h-full">
                        <div class="w-16 h-24 flex-shrink-0 bg-surface-variant shadow-sm rounded overflow-hidden border border-[#113819]/10">
                            {% if loan.cover_image %}
                            <img src="{{ loan.cover_image }}" alt="{{ loan.Title }}" class="w-full h-full object-cover">
                            {% else %}
                            <div class="w-full h-full flex items-center justify-center bg-stone-200 text-stone-400">
                                <span class="material-symbols-outlined text-xl">book</span>
                            </div>
                            {% endif %}
                        </div>
                        <div class="flex-grow flex flex-col justify-between py-1 w-full text-left">
                            <div>
                                <div class="flex flex-wrap items-center justify-start gap-2 mb-1">
                                    <h3 class="font-headline text-sm font-bold text-primary-container leading-tight line-clamp-2">{{ loan.Title }}</h3>
                                    {% if loan.IsOverdue %}
                                    <span class="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-[9px] font-headline font-bold uppercase tracking-widest inline-block">Overdue</span>
                                    {% else %}
                                    <span class="px-2 py-0.5 bg-secondary-container text-on-secondary-container rounded-full text-[9px] font-headline font-bold uppercase tracking-widest inline-block">Active</span>
                                    {% endif %}
                                </div>
                                <p class="font-body text-xs italic text-on-surface-variant mb-2 line-clamp-1">{{ loan.Authors or 'Unknown Author' }}</p>
                                <div class="grid grid-cols-2 gap-2">
                                    <div>
                                        <p class="text-[9px] font-headline font-bold uppercase tracking-widest text-[#113819]/40 mb-0.5">Borrowed</p>
                                        <p class="font-body text-xs font-medium">{{ loan.IssueDate.strftime('%b %d') if loan.IssueDate else '—' }}</p>
                                    </div>
                                    <div>
                                        <p class="text-[9px] font-headline font-bold uppercase tracking-widest text-[#113819]/40 mb-0.5">Due</p>
                                        <p class="font-body text-xs font-medium {{ 'text-red-700 font-bold' if loan.IsOverdue else '' }}">{{ loan.DueDate.strftime('%b %d') if loan.DueDate else '—' }}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-3 flex justify-start gap-2">
                                <form action="{{ url_for('loans.return_book', loan_id=loan.LoanID) }}" method="POST">
                                    <button type="submit" class="bg-primary-container text-[#f5eebf] px-3 py-1.5 rounded font-headline text-xs font-bold tracking-tight hover:opacity-90 transition-opacity">Return</button>
                                </form>
                            </div>
                        </div>
                    </div>"""

# Remove the Renew button from template, wait I should include the Renew button just in case but match the regex. I updated the regex to catch it, so the replacement will omit it. No, keep it.
compact_loan_card = compact_loan_card.replace('</form>', '</form>\n                                <button class="border border-[#113819]/20 text-primary-container px-3 py-1.5 rounded font-headline text-xs font-bold tracking-tight hover:bg-surface-container-high transition-colors">Renew</button>')

content = loan_card_regex.sub(compact_loan_card, content)

# Update the summary line
header_regex = re.compile(r'<div class="flex justify-between items-center mb-8 border-b border-\[#113819\]/5 pb-4">.*?<h2 class="font-headline text-3xl font-bold text-primary-container tracking-tight">Active Loans</h2>.*?<div id="loan-count-text" class="text-sm font-headline font-semibold text-primary-container/60 italic">.*?Showing 1-\{\{ \[loans\|length, 6\]\|min \}\} of \{\{ loans\|length \}\} loans.*?</div>.*?</div>', re.DOTALL)

summary_html = """<div class="flex justify-between items-center mb-6 border-b border-[#113819]/5 pb-4">
                <h2 class="font-headline text-3xl font-bold text-primary-container tracking-tight">Active Loans</h2>
                <div id="loan-count-text" class="text-sm font-headline text-primary-container/80 font-medium">
                    {{ loans|length }} active loans — {{ loans|selectattr('IsOverdue', 'equalto', true)|list|length }} overdue
                </div>
            </div>"""
content = header_regex.sub(summary_html, content)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard updated")
