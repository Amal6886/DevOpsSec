from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Supplement, ProteinBar
from .forms import SupplementForm, ProteinBarForm


def product_list(request):
    supplements = Supplement.objects.all()
    protein_bars = ProteinBar.objects.all()

    context = {
        'supplements': supplements,
        'protein_bars': protein_bars,
    }
    return render(request, 'products/product_list.html', context)


def supplement_detail(request, pk):
    supplement = get_object_or_404(Supplement, pk=pk)
    return render(
        request,
        'products/product_detail.html',
        {'product': supplement, 'product_type': 'supplement'}
    )


def protein_bar_detail(request, pk):
    protein_bar = get_object_or_404(ProteinBar, pk=pk)
    return render(
        request,
        'products/product_detail.html',
        {'product': protein_bar, 'product_type': 'protein_bar'}
    )


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin_product_list(request):
    supplements = Supplement.objects.all()
    protein_bars = ProteinBar.objects.all()

    context = {
        'supplements': supplements,
        'protein_bars': protein_bars,
    }
    return render(request, 'products/admin/product_list.html', context)


@user_passes_test(is_admin)
def create_supplement(request):
    if request.method == 'POST':
        form = SupplementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplement created successfully!')
            return redirect('products:admin_product_list')
    else:
        form = SupplementForm()
    return render(request, 'products/admin/product_form.html', {'form': form, 'product_type': 'Supplement'})


@user_passes_test(is_admin)
def update_supplement(request, pk):
    supplement = get_object_or_404(Supplement, pk=pk)
    if request.method == 'POST':
        form = SupplementForm(request.POST, request.FILES, instance=supplement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplement updated successfully!')
            return redirect('products:admin_product_list')
    else:
        form = SupplementForm(instance=supplement)
    return render(
        request,
        'products/admin/product_form.html',
        {
            'form': form,
            'product': supplement,
            'product_type': 'Supplement'
        }
    )


@user_passes_test(is_admin)
def delete_supplement(request, pk):
    supplement = get_object_or_404(Supplement, pk=pk)
    if request.method == 'POST':
        supplement.delete()
        messages.success(request, 'Supplement deleted successfully!')
        return redirect('products:admin_product_list')
    return render(
        request,
        'products/admin/product_confirm_delete.html',
        {'product': supplement, 'product_type': 'Supplement'}
    )


@user_passes_test(is_admin)
def create_protein_bar(request):
    if request.method == 'POST':
        form = ProteinBarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Protein bar created successfully!')
            return redirect('products:admin_product_list')
    else:
        form = ProteinBarForm()
    return render(request, 'products/admin/product_form.html', {'form': form, 'product_type': 'Protein Bar'})


@user_passes_test(is_admin)
def update_protein_bar(request, pk):
    protein_bar = get_object_or_404(ProteinBar, pk=pk)
    if request.method == 'POST':
        form = ProteinBarForm(request.POST, request.FILES, instance=protein_bar)
        if form.is_valid():
            form.save()
            messages.success(request, 'Protein bar updated successfully!')
            return redirect('products:admin_product_list')
    else:
        form = ProteinBarForm(instance=protein_bar)
    return render(
        request,
        'products/admin/product_form.html',
        {
            'form': form,
            'product': protein_bar,
            'product_type': 'Protein Bar'
        }
    )


@user_passes_test(is_admin)
def delete_protein_bar(request, pk):
    protein_bar = get_object_or_404(ProteinBar, pk=pk)
    if request.method == 'POST':
        protein_bar.delete()
        messages.success(request, 'Protein bar deleted successfully!')
        return redirect('products:admin_product_list')
    return render(
        request,
        'products/admin/product_confirm_delete.html',
        {'product': protein_bar, 'product_type': 'Protein Bar'}
    )
