/**
 * Profiles Management Module
 * Handles profile listing, creation, editing, and deletion functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const profilesContent = document.getElementById('profiles-content');
    const searchInput = document.getElementById('search-profiles');
    
    // Store all profiles for filtering
    let allProfiles = [];
    
    /**
     * Renders the profiles list in the DOM
     * @param {Array} profiles - Array of profile objects to render
     */
    function renderProfiles(profiles) {
        const profilesList = document.getElementById('profiles-list');
        profilesList.innerHTML = '';
        
        if (profiles.length === 0) {
            profilesList.innerHTML = '<div class="text-muted text-center p-4 rounded" style="background-color: var(--bg-secondary); border: 1px solid var(--border-color);">No profiles to show.</div>';
        } else {
            profiles.forEach((profile, index) => {
                const profileItem = document.createElement('div');
                profileItem.className = 'list-group-item list-group-item-light d-flex justify-content-between align-items-center';
                
                profileItem.innerHTML = `
                    <div class="d-flex align-items-center flex-grow-1">
                        <div class="profile-icon me-3" style="
                            width: 48px;
                            height: 48px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius: 12px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-weight: bold;
                            font-size: 1.2rem;
                        ">
                            <i class="bi bi-collection"></i>
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="mb-1" style="color: var(--text-primary);">${profile.name}</h6>
                            <div class="${profile.step_count > 0 ? 'text-info' : 'text-muted'}" style="font-size: 0.85rem;">
                                <i class="bi bi-list-task me-1"></i>
                                ${profile.step_count} setup step${profile.step_count !== 1 ? 's' : ''}
                            </div>
                            <div class="mt-1" style="font-size: 0.8rem;">
                                <div class="${profile.total_computers > 0 ? 'text-info' : 'text-muted'}">
                                    <i class="bi bi-pc-display me-1"></i>
                                    ${profile.total_computers} computer${profile.total_computers !== 1 ? 's' : ''}
                                </div>
                            </div>
                            <div class="mt-1 ${profile.attributes_count > 0 ? 'text-info' : 'text-muted'}" style="font-size: 0.8rem;">
                                <i class="bi bi-tag me-1"></i>
                                ${profile.attributes_count} attribute${profile.attributes_count !== 1 ? 's' : ''}
                            </div>
                        </div>
                    </div>
                    <div class="d-flex flex-column gap-2">
                        <button class="btn btn-sm btn-outline-secondary" onclick="editProfile(${profile.id})" style="
                            border-color: var(--accent-purple);
                            color: var(--accent-purple);
                            transition: all 0.3s ease;
                        " onmouseover="this.style.backgroundColor='var(--accent-purple)'; this.style.color='white';" onmouseout="this.style.backgroundColor='transparent'; this.style.color='var(--accent-purple)';">
                            <i class="bi bi-pencil"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="confirmDeleteProfile(${profile.id}, '${profile.name}')">
                            <i class="bi bi-trash"></i> Delete
                        </button>
                    </div>
                `;
                profilesList.appendChild(profileItem);
            });
        }
    }
    
    /**
     * Filters profiles based on search term
     * @param {string} searchTerm - The search term to filter by
     */
    function filterProfiles(searchTerm) {
        const filteredProfiles = allProfiles.filter(profile => 
            profile.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
        renderProfiles(filteredProfiles);
    }
    
    /**
     * Loads all profiles from the API
     */
    function loadProfiles() {
        loadingSpinner.style.display = 'block';
        errorContainer.style.display = 'none';
        profilesContent.style.display = 'none';
        
        fetch('/api/profiles')
            .then(response => response.json())
            .then(data => {
                if (data.Error) {
                    throw new Error(data.Error);
                }
                
                // Store all profiles
                allProfiles = data;
                
                // Show "No profiles available" message if no profiles exist
                if (data.length === 0) {
                    const profilesList = document.getElementById('profiles-list');
                    profilesList.innerHTML = '<div class="text-muted text-center p-4 rounded" style="background-color: var(--bg-secondary); border: 1px solid var(--border-color);">No profiles available. Create your first profile to get started.</div>';
                } else {
                    // Apply current search filter
                    const searchTerm = searchInput.value;
                    filterProfiles(searchTerm);
                }
                
                // Show content
                loadingSpinner.style.display = 'none';
                profilesContent.style.display = 'block';
            })
            .catch(error => {
                console.error('Error loading profiles:', error);
                errorMessage.textContent = error.message || 'Failed to load profiles. Please try again later.';
                loadingSpinner.style.display = 'none';
                errorContainer.style.display = 'block';
            });
    }
    
    /**
     * Redirects to profile editing page
     * @param {number} profileId - The ID of the profile to edit
     */
    function editProfile(profileId) {
        window.location.href = `/edit-profile/${profileId}`;
    }
    
    /**
     * Creates a new profile
     */
    function createNewProfile() {
        // For now, just redirect to a placeholder
        const profileName = prompt('Enter profile name:');

        if (!profileName) {
            showToast('Profile name is required!', 'error');
            return;
        }

        fetch('/api/add_profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: profileName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Profile created successfully!', 'success');
                loadProfiles();
            } else {
                showToast('Error creating profile: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An unexpected error occurred while creating the profile.', 'error');
        });
    }
    
    /**
     * Shows confirmation modal for profile deletion
     * @param {number} profileId - The ID of the profile to delete
     * @param {string} profileName - The name of the profile to delete
     */
    function confirmDeleteProfile(profileId, profileName) {
        // Set the profile name in the modal
        document.getElementById('deleteProfileName').textContent = profileName;
        
        // Fetch computers using this profile
        console.log('Fetching computers for profile ID:', profileId);
        
        fetch(`/api/profile/${profileId}/computers`)
            .then(response => {
                console.log('Computers response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Computers data:', data);
                
                const computersContainer = document.getElementById('computersToDelete');
                computersContainer.innerHTML = '';
                
                if (data.computers && data.computers.length > 0) {
                    // Show computers list
                    const computersList = document.createElement('div');
                    computersList.className = 'list-group';
                    computersList.style.maxHeight = '200px';
                    computersList.style.overflowY = 'auto';
                    
                    data.computers.forEach(computer => {
                        const computerItem = document.createElement('div');
                        computerItem.className = 'list-group-item d-flex align-items-center';
                        computerItem.style.cssText = `
                            background-color: var(--bg-secondary);
                            border-color: var(--border-color);
                            color: var(--text-primary);
                        `;
                        computerItem.innerHTML = `
                            <i class="bi bi-pc-display me-2 text-danger"></i>
                            <span>${computer.name}</span>
                        `;
                        computersList.appendChild(computerItem);
                    });
                    
                    computersContainer.appendChild(computersList);
                } else {
                    // No computers using this profile
                    const noComputersMsg = document.createElement('div');
                    noComputersMsg.className = 'text-muted text-center p-3';
                    noComputersMsg.style.cssText = `
                        background-color: var(--bg-secondary);
                        border: 1px solid var(--border-color);
                        border-radius: 8px;
                    `;
                    noComputersMsg.innerHTML = `
                        <i class="bi bi-info-circle me-2"></i>
                        No computers are currently using this profile.
                    `;
                    computersContainer.appendChild(noComputersMsg);
                }
                
                // Store the profile ID for deletion
                window.currentProfileToDelete = profileId;
                
                // Show the modal
                const modal = new bootstrap.Modal(document.getElementById('deleteProfileModal'));
                modal.show();
            })
            .catch(error => {
                console.error('Error fetching computers for profile:', error);
                
                // Show modal anyway, but with error message for computers
                const computersContainer = document.getElementById('computersToDelete');
                computersContainer.innerHTML = '';
                
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-warning';
                errorMsg.innerHTML = `
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Could not load computers for this profile. The profile will still be deleted.
                `;
                computersContainer.appendChild(errorMsg);
                
                // Store the profile ID for deletion
                window.currentProfileToDelete = profileId;
                
                // Show the modal
                const modal = new bootstrap.Modal(document.getElementById('deleteProfileModal'));
                modal.show();
            });
    }
    
    /**
     * Deletes a profile
     * @param {number} profileId - The ID of the profile to delete
     */
    function deleteProfile(profileId) {
        const deleteBtn = document.getElementById('executeDeleteProfile');
        
        // Show loading state
        deleteBtn.disabled = true;
        deleteBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Deleting...';
        
        console.log('Attempting to delete profile with ID:', profileId);
        
        fetch(`/api/profile/${profileId}/delete`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            console.log('Delete response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Delete response data:', data);
            
            if (data.success) {
                // Hide the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteProfileModal'));
                modal.hide();
                
                // Show success message
                showToast('Profile and associated computers deleted successfully!', 'success');
                
                // Reload profiles
                loadProfiles();
            } else {
                showToast('Error deleting profile: ' + (data.message || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting profile:', error);
            showToast('Error deleting profile. Please try again.', 'error');
        })
        .finally(() => {
            // Reset button state
            deleteBtn.disabled = false;
            deleteBtn.innerHTML = '<i class="bi bi-trash"></i> Delete Profile';
        });
    }
    
    // Make functions available globally
    window.editProfile = editProfile;
    window.createNewProfile = createNewProfile;
    window.confirmDeleteProfile = confirmDeleteProfile;
    window.deleteProfile = deleteProfile;

    // Connect the add profile button
    document.getElementById('add-profile-btn').addEventListener('click', createNewProfile);
    
    // Add search input event listener
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value;
        filterProfiles(searchTerm);
    });
    
    // Modal event listeners
    document.getElementById('confirmDeleteProfile').addEventListener('change', function() {
        const executeBtn = document.getElementById('executeDeleteProfile');
        executeBtn.disabled = !this.checked;
    });
    
    document.getElementById('executeDeleteProfile').addEventListener('click', function() {
        if (window.currentProfileToDelete) {
            deleteProfile(window.currentProfileToDelete);
        }
    });
    
    // Reset modal when it's closed
    document.getElementById('deleteProfileModal').addEventListener('hidden.bs.modal', function() {
        document.getElementById('confirmDeleteProfile').checked = false;
        document.getElementById('executeDeleteProfile').disabled = true;
        window.currentProfileToDelete = null;
    });

    // Load initial data
    loadProfiles();
});
