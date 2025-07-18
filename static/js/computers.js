document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('computer-cards');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noComputersMessage = document.getElementById('no-computers-message');
    const technicianFilter = document.getElementById('technicianFilter');
    const computerSearch = document.getElementById('computerSearch');
    let isLoading = false; // Flag to prevent multiple requests
    let allComputers = []; // Store all computer data for filtering
    let currentFilterId = 0; // Track current filter operation to avoid race conditions
    let selectedFilterTechnicianIds = []; // Store selected technician IDs for filtering
    
    // Toast notification function
    function showToast(message, type = 'success') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'position-fixed top-0 end-0 p-3 toast-container';
            toastContainer.style.zIndex = '9999';
            toastContainer.style.pointerEvents = 'none';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const alertClass = type === 'error' ? 'danger' : 'success';
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `alert alert-${alertClass} alert-dismissible fade show`;
        toast.setAttribute('role', 'alert');
        toast.style.pointerEvents = 'auto';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add toast to container
        toastContainer.appendChild(toast);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (document.getElementById(toastId)) {
                toast.classList.remove('show');
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 150);
            }
        }, 10000);
    }

    function loadComputers() {
        if (isLoading) {
            console.log('loadComputers() called while already loading, skipping...');
            return; // Exit if a request is already in progress
        }
        
        isLoading = true;
        loadingSpinner.style.display = 'block';
        
        // Clear the container immediately to prevent duplicates
        container.innerHTML = '';
        
        // Increment filter ID to invalidate any pending filter operations
        currentFilterId++;

        fetch('/api/computers')
            .then(response => response.json())
            .then(computers => {
                allComputers = computers;
                filterComputers();
                populateTechnicians();
            })
            .catch((error) => {
                console.error('Error loading computers:', error);
                showToast('Error loading computers', 'error');
            })
            .finally(() => {
                isLoading = false;
                loadingSpinner.style.display = 'none';
            });
    }

    computerSearch.addEventListener('input', filterComputers);
    
    // Add event listeners for completion status filters
    document.getElementById('showCompleted').addEventListener('change', filterComputers);
    document.getElementById('showIncomplete').addEventListener('change', filterComputers);

    // Function to get deadline styling based on time remaining
    function getDeadlineStyle(deadlineStr) {
        if (!deadlineStr || deadlineStr === 'Not set') {
            return { text: 'Not set', class: '', color: '' };
        }

        const now = new Date();
        const deadline = new Date(deadlineStr);
        const timeDiff = deadline - now;
        const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));

        // Format deadline as dd/mm/yy at hh:mm
        const day = String(deadline.getDate()).padStart(2, '0');
        const month = String(deadline.getMonth() + 1).padStart(2, '0');
        const year = String(deadline.getFullYear()).slice(-2);
        const hours = String(deadline.getHours()).padStart(2, '0');
        const minutes = String(deadline.getMinutes()).padStart(2, '0');
        const formattedDate = `${day}/${month}/${year} at ${hours}:${minutes}`;

        let text = formattedDate;
        let colorClass = '';
        let style = '';

        if (timeDiff < 0) {
            // Overdue
            text = `${formattedDate} (overdue)`;
            colorClass = 'text-danger';
            style = 'color: #dc3545; font-weight: bold;';
        } else if (daysDiff === 0) {
            // Same day
            colorClass = 'text-danger';
            style = 'color: #dc3545; font-weight: bold;';
        } else if (daysDiff < 7) {
            // Less than a week
            colorClass = 'text-warning';
            style = 'color: #fd7e14; font-weight: bold;';
        } else {
            // More than a week
            colorClass = 'text-success';
            style = 'color: #198754; font-weight: bold;';
        }

        return { text, class: colorClass, style };
    }

    function filterComputers() {
        const searchTerm = computerSearch.value.toLowerCase().trim();
        const showCompleted = document.getElementById('showCompleted').checked;
        const showIncomplete = document.getElementById('showIncomplete').checked;
        
        // Increment filter ID to track this specific filter operation
        const filterId = ++currentFilterId;
        
        // Clear container and reset state
        container.innerHTML = '';
        noComputersMessage.style.display = 'none';
        
        // If both completion status filters are disabled, show no computers message
        if (!showCompleted && !showIncomplete) {
            noComputersMessage.style.display = 'block';
            return;
        }
        
        const filteredComputers = allComputers.filter(computer => {
            // Filter by technicians - if no technicians selected, show all
            let technicianMatch = true;
            if (selectedFilterTechnicianIds.length > 0) {
                // Check if computer has any of the selected technicians
                technicianMatch = selectedFilterTechnicianIds.some(selectedId => {
                    // Check both the old single technician_id and new multiple technicians
                    if (computer.technician_id === selectedId) {
                        return true;
                    }
                    // Check if computer has technicians array (new multi-technician support)
                    if (computer.technicians && Array.isArray(computer.technicians)) {
                        return computer.technicians.some(tech => tech.id === selectedId);
                    }
                    return false;
                });
            }
            
            // Filter by name search - using startsWith instead of includes
            const nameMatch = !searchTerm || computer.name.toLowerCase().startsWith(searchTerm);
            
            return technicianMatch && nameMatch;
        });
        
        // If no computers to display, return early
        if (filteredComputers.length === 0) {
            noComputersMessage.style.display = 'block';
            return;
        }

        // Track how many computers actually get displayed after all filters
        let displayedCount = 0;
        let processedCount = 0;
        const totalToProcess = filteredComputers.length;
        
        // Function to check if we should show the no computers message
        function checkNoComputersMessage() {
            if (processedCount === totalToProcess && displayedCount === 0) {
                noComputersMessage.style.display = 'block';
            }
        }

        filteredComputers.forEach((computer, index) => {
            setTimeout(() => {
                fetch(`/api/computer_info/${computer.id}`)
                    .then(response => response.json())
                    .then(computerData => {
                    processedCount++;
                    
                    // Only add card if this is still the current filter operation
                    if (!computerData.Error && filterId === currentFilterId) {
                        const card = document.createElement('div');
                        card.className = 'col-lg-4 col-md-6 col-sm-12 mb-4';
                        let completed = parseInt(computerData.completed_steps_num) || 0;
                        let total = parseInt(computerData.total_step_num) || 0;
                        let progressPercentage = total > 0 ? Math.round((completed / total) * 100) : 0;
                        
                        // Check completion status filter
                        const isCompleted = progressPercentage === 100;
                        const showCompleted = document.getElementById('showCompleted').checked;
                        const showIncomplete = document.getElementById('showIncomplete').checked;
                        
                        // Skip this computer if it doesn't match the completion status filter
                        if ((isCompleted && !showCompleted) || (!isCompleted && !showIncomplete)) {
                            checkNoComputersMessage();
                            return;
                        }
                        
                        displayedCount++;
                        
                        // Get deadline styling
                        const deadlineStyle = getDeadlineStyle(computerData.deadline);
                        
                        card.innerHTML = `
                            <div class="card h-100">
                                <div class="card-header">
                                    <h5 class="card-title mb-0">${computerData.name}</h5>
                                </div>
                                <div class="card-body d-flex flex-column">
                                    <p class="mb-2"><strong>Profile:</strong> ${computerData.profile ? computerData.profile.name : 'No profile'}</p>
                                    <p class="mb-2"><strong>Technician${computerData.technicians && computerData.technicians.length > 1 ? 's' : ''}:</strong> ${computerData.technicians && computerData.technicians.length > 0 ? computerData.technicians.map(tech => tech.name).join(', ') : 'Unassigned'}</p>
                                    <p class="mb-2"><strong>Deadline:</strong> <span class="${deadlineStyle.class}" style="${deadlineStyle.style}">${deadlineStyle.text}</span></p>
                                    <p class="mb-3"><strong>Steps:</strong> ${completed}/${total} completed</p>
                                    <div class="progress-section mb-3">
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <span class="progress-label">Setup Progress</span>
                                            <span class="progress-percentage">${progressPercentage}%</span>
                                        </div>
                                        <div class="custom-progress-bar">
                                            <div class="progress-fill" style="width: ${progressPercentage}%"></div>
                                        </div>
                                    </div>
                                    <div class="mt-auto">
                                        <a href="/setup/${computerData.id}" class="btn btn-primary w-100">
                                            <i class="bi bi-arrow-right"></i> Continue Setup
                                        </a>
                                    </div>
                                </div>
                            </div>
                        `;
                        container.appendChild(card);
                    } else {
                        // Computer data has error or filter ID changed
                        checkNoComputersMessage();
                    }
                })
                .catch(error => {
                    console.error('Error fetching computer info:', error);
                    processedCount++;
                    checkNoComputersMessage();
                });
            }, index * 50); // 50ms delay between each request
        });
    }

    function populateTechnicians() {
        fetch('/api/technicians')
            .then(response => response.json())
            .then(technicians => {
                if (!technicians.Error) {
                    // Clear the container
                    technicianFilter.innerHTML = '';
                    
                    if (technicians.length === 0) {
                        technicianFilter.innerHTML = '<div class="text-muted text-center" style="padding: 10px; font-style: italic;">No technicians available</div>';
                        return;
                    }
                    
                    // Create technician cards for filtering
                    technicians.forEach(technician => {
                        const technicianCard = document.createElement('div');
                        technicianCard.className = 'technician-card filter-card';
                        technicianCard.textContent = technician.name;
                        technicianCard.dataset.technicianId = technician.id;
                        technicianCard.dataset.technicianName = technician.name;
                        
                        // Add click event listener for filter selection
                        technicianCard.addEventListener('click', function() {
                            toggleFilterTechnicianSelection(this);
                        });
                        
                        technicianFilter.appendChild(technicianCard);
                    });
                } else {
                    technicianFilter.innerHTML = '<div class="text-danger text-center" style="padding: 10px;">Error loading technicians</div>';
                }
            })
            .catch(error => {
                console.error('Error fetching technicians:', error);
                technicianFilter.innerHTML = '<div class="text-danger text-center" style="padding: 10px;">Error loading technicians</div>';
            });
    }

    // Toggle filter technician selection
    function toggleFilterTechnicianSelection(cardElement) {
        const technicianId = parseInt(cardElement.dataset.technicianId);
        const isSelected = cardElement.classList.contains('selected');
        
        if (isSelected) {
            // Deselect technician
            cardElement.classList.remove('selected');
            selectedFilterTechnicianIds = selectedFilterTechnicianIds.filter(id => id !== technicianId);
        } else {
            // Select technician
            cardElement.classList.add('selected');
            selectedFilterTechnicianIds.push(technicianId);
        }
        
        // Update hidden input for consistency
        const hiddenInput = document.getElementById('selectedFilterTechnicianIds');
        if (hiddenInput) {
            hiddenInput.value = selectedFilterTechnicianIds.join(',');
        }
        
        // Update the filter label
        updateFilterTechnicianLabel();
        
        // Apply the filter
        filterComputers();
    }
    
    // Update the filter technician label to show selection count
    function updateFilterTechnicianLabel() {
        const label = document.querySelector('label[for="technicianFilter"]');
        const selectedCount = selectedFilterTechnicianIds.length;
        
        if (selectedCount === 0) {
            label.textContent = 'Filter by Technicians:';
        } else if (selectedCount === 1) {
            const selectedCard = document.querySelector('.technician-card.filter-card.selected');
            label.textContent = `Filter by Technician: ${selectedCard.dataset.technicianName}`;
        } else {
            label.textContent = `Filter by Technicians (${selectedCount} selected):`;
        }
    }
    
    // Load all computers at once
    loadComputers();

    // Modal functionality
    const addComputerBtn = document.getElementById('add-computer-btn');
    const addComputerModal = document.getElementById('addComputerModal');
    const submitComputerBtn = document.getElementById('submit-computer');
    const addComputerForm = document.getElementById('add-computer-form');
    const closeButtons = document.querySelectorAll('[data-dismiss="modal"]');

    // Function to populate dropdowns
    function populateDropdowns() {
        // Populate profiles dropdown
        fetch('/api/profiles')
            .then(response => response.json())
            .then(profiles => {
                const profileSelect = document.getElementById('profileId');
                profileSelect.innerHTML = '<option value="">Select a profile...</option>';
                
                if (profiles.Error) {
                    console.error('Error fetching profiles:', profiles.Error);
                    profileSelect.innerHTML += '<option value="" disabled>Error loading profiles</option>';
                } else {
                    profiles.forEach(profile => {
                        const option = document.createElement('option');
                        option.value = profile.id;
                        option.textContent = `${profile.name}${profile.description ? ' - ' + profile.description : ''}`;
                        profileSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching profiles:', error);
                const profileSelect = document.getElementById('profileId');
                profileSelect.innerHTML += '<option value="" disabled>Error loading profiles</option>';
            });

        // Populate technicians selection
        fetch('/api/technicians')
            .then(response => response.json())
            .then(technicians => {
                const technicianContainer = document.getElementById('technicianSelection');
                technicianContainer.innerHTML = '';
                
                if (technicians.Error) {
                    console.error('Error fetching technicians:', technicians.Error);
                    technicianContainer.innerHTML = '<div class="text-danger text-center" style="padding: 20px;">Error loading technicians</div>';
                } else if (technicians.length === 0) {
                    technicianContainer.innerHTML = '<div class="text-muted text-center" style="padding: 20px; font-style: italic;">No technicians available</div>';
                } else {
                    technicians.forEach(technician => {
                        const technicianCard = document.createElement('div');
                        technicianCard.className = 'technician-card';
                        technicianCard.textContent = technician.name;
                        technicianCard.dataset.technicianId = technician.id;
                        technicianCard.dataset.technicianName = technician.name;
                        
                        // Add click event listener
                        technicianCard.addEventListener('click', function() {
                            toggleTechnicianSelection(this);
                        });
                        
                        technicianContainer.appendChild(technicianCard);
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching technicians:', error);
                const technicianContainer = document.getElementById('technicianSelection');
                technicianContainer.innerHTML = '<div class="text-danger text-center" style="padding: 20px;">Error loading technicians</div>';
            });
    }
    
    // Toggle technician selection
    function toggleTechnicianSelection(cardElement) {
        const technicianId = parseInt(cardElement.dataset.technicianId);
        const isSelected = cardElement.classList.contains('selected');
        
        if (isSelected) {
            // Deselect technician
            cardElement.classList.remove('selected');
        } else {
            // Select technician
            cardElement.classList.add('selected');
        }
        
        // Update the hidden input with selected technician IDs
        updateSelectedTechnicians();
        
        // Update the label to show selection count
        updateTechnicianLabel();
    }
    
    // Update the hidden input with selected technician IDs
    function updateSelectedTechnicians() {
        const selectedCards = document.querySelectorAll('.technician-card.selected');
        const selectedIds = Array.from(selectedCards).map(card => parseInt(card.dataset.technicianId));
        const hiddenInput = document.getElementById('selectedTechnicianIds');
        hiddenInput.value = selectedIds.join(',');
    }
    
    // Update the technician label to show selection count
    function updateTechnicianLabel() {
        const selectedCards = document.querySelectorAll('.technician-card.selected');
        const selectedCount = selectedCards.length;
        const label = document.querySelector('label[for="technicianSelection"]');
        
        if (selectedCount > 0) {
            const selectedNames = Array.from(selectedCards).map(card => card.dataset.technicianName);
            if (selectedCount === 1) {
                label.textContent = `Technician: ${selectedNames[0]}`;
            } else {
                label.textContent = `Technicians (${selectedCount} selected)`;
            }
        } else {
            label.textContent = 'Technicians';
        }
    }
    
    // Show modal
    addComputerBtn.addEventListener('click', function() {
        addComputerModal.classList.add('show');
        document.body.classList.add('modal-open');
        
        // Populate dropdowns when modal opens
        populateDropdowns();
    });

    // Hide modal
    function hideModal() {
        addComputerModal.classList.remove('show');
        document.body.classList.remove('modal-open');
        addComputerForm.reset();
        
        // Reset technician selections
        const selectedCards = document.querySelectorAll('.technician-card.selected');
        selectedCards.forEach(card => {
            card.classList.remove('selected');
        });
        
        // Reset the hidden input
        const hiddenInput = document.getElementById('selectedTechnicianIds');
        if (hiddenInput) {
            hiddenInput.value = '';
        }
        
        // Reset the technician label
        const label = document.querySelector('label[for="technicianSelection"]');
        if (label) {
            label.textContent = 'Technicians';
        }
    }

    // Close modal events
    closeButtons.forEach(button => {
        button.addEventListener('click', hideModal);
    });

    // Close modal when clicking outside
    addComputerModal.addEventListener('click', function(e) {
        if (e.target === addComputerModal) {
            hideModal();
        }
    });

    // Handle form submission
    submitComputerBtn.addEventListener('click', function() {
        const selectedTechnicianIds = document.getElementById('selectedTechnicianIds').value;
        const technicianIds = selectedTechnicianIds ? selectedTechnicianIds.split(',').map(id => parseInt(id)) : [];
        
        const formData = {
            name: document.getElementById('computerName').value,
            deadline: document.getElementById('computerDeadline').value,
            profile_id: parseInt(document.getElementById('profileId').value),
            technician_ids: technicianIds
        };
        
        console.log('Form data before validation:', formData);

        // Basic validation
        if (!formData.name || !formData.deadline || !formData.profile_id || !formData.technician_ids.length) {
            showToast('Please fill in all fields and select at least one technician', 'error');
            return;
        }

        // Additional validation for numeric fields
        if (isNaN(formData.profile_id) || formData.profile_id <= 0 || 
            formData.technician_ids.some(id => isNaN(id) || id <= 0)) {
            showToast('Please select valid profile and technicians', 'error');
            return;
        }

        // Convert datetime-local to the expected format
        try {
            const dateObject = new Date(formData.deadline);
            if (isNaN(dateObject.getTime())) {
                showToast('Please enter a valid deadline date and time', 'error');
                return;
            }
            // Format as YYYY-MM-DD HH:MM:SS for database storage
            formData.deadline = dateObject.getFullYear() + '-' + 
                               String(dateObject.getMonth() + 1).padStart(2, '0') + '-' + 
                               String(dateObject.getDate()).padStart(2, '0') + ' ' + 
                               String(dateObject.getHours()).padStart(2, '0') + ':' + 
                               String(dateObject.getMinutes()).padStart(2, '0') + ':' + 
                               String(dateObject.getSeconds()).padStart(2, '0');
        } catch (error) {
            showToast('Please enter a valid deadline date and time', 'error');
            return;
        }

        // Show loading state
        submitComputerBtn.disabled = true;
        submitComputerBtn.textContent = 'Adding...';

        // Send request to API
        fetch('/api/add_computer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                // Handle non-200 responses
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return response.json().then(errorData => {
                        if (response.status === 409) {
                            // Handle duplicate computer name error
                            throw new Error('A computer with this name already exists. Please choose a different name.');
                        }
                        // Handle other JSON errors
                        throw new Error(errorData.Error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
                    });
                } else {
                    // Handle HTML error pages (like CSRF errors)
                    return response.text().then(htmlText => {
                        if (htmlText.includes('CSRF') || htmlText.includes('csrf')) {
                            throw new Error('Security token expired. Please refresh the page and try again.');
                        }
                        throw new Error(`Server error (${response.status}): Please try again or contact support.`);
                    });
                }
            }
            return response.json();
        })
        .then(data => {
            if (data.message) {
                showToast('Computer added successfully!', 'success');
                hideModal();
                // Reload the computers list
                loadComputers();
            } else if (data.Error) {
                showToast('Error: ' + data.Error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error: ' + (error.message || 'An error occurred while adding the computer'), 'error');
        })
        .finally(() => {
            // Reset button state
            submitComputerBtn.disabled = false;
            submitComputerBtn.textContent = 'Add Computer';
        });
    });
});
